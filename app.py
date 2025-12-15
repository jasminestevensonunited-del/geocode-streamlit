import streamlit as st
import requests
import urllib.parse

STATE = "TN"

def get_geocode_data(address, api_key):
    encoded_address = urllib.parse.quote_plus(address)
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={encoded_address}&key={api_key}"
    response = requests.get(url, timeout=10)
    if response.status_code != 200:
        return None
    return response.json()

def extract_all_components(components):
    extracted = {}
    for comp in components:
        for type_name in comp["types"]:
            extracted[type_name] = comp["short_name"]
    return extracted

st.set_page_config(page_title="TN Address Geocoder", layout="centered")

st.title("Address Geocoder (TN)")

# Prefer API key from Streamlit secrets; fall back to input if not provided
api_key = st.secrets.get("GOOGLE_API_KEY", None) or st.text_input("Google API Key", type="password")

street = st.text_input("Street Address", placeholder="123 Main St")
city = st.text_input("City", placeholder="Nashville")

if st.button("Geocode Address"):
    if not api_key:
        st.error("Please enter your Google API key; or add it to Streamlit secrets.")
    elif not street or not city:
        st.error("Please enter both street and city.")
    else:
        full_address = f"{street}, {city}, {STATE}"
        with st.spinner("Contacting Google Geocoding API..."):
            data = get_geocode_data(full_address, api_key)

        if not data or data.get("status") != "OK":
            st.error("Could not retrieve geocode data; check the address or API key/quotas.")
        else:
            result = data["results"][0]
            components = result["address_components"]
            location = result["geometry"]["location"]
            extracted = extract_all_components(components)

            # Build the full street address
            street_parts = []
            if "street_number" in extracted:
                street_parts.append(extracted["street_number"])
            if "route" in extracted:
                street_parts.append(extracted["route"])
            for key in ["subpremise", "premise", "sublocality"]:
                if key in extracted:
                    street_parts.append(extracted[key])
            full_street = " ".join(street_parts)

            st.success("Geocoding Successful!")

            st.write("### 📍 Address Details")
            st.write(f"**Full Street Address:** {full_street}")
            st.write(f"**City:** {extracted.get('locality', '')}")
            st.write(f"**County:** {extracted.get('administrative_area_level_2', '')}")
            st.write(f"**ZIP Code:** {extracted.get('postal_code', '')}")

            st.write("### 🌐 Coordinates")
            st.write(f"**Latitude:** {location['lat']}")
            st.write(f"**Longitude:** {location['lng']}")

            with st.expander("Full JSON Response"):
                st.json(result)
