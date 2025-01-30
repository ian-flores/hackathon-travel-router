import streamlit as st

import folium
from streamlit_folium import st_folium
import pandas as pd
import ai

st.set_page_config(layout="wide")

def main():
    st.title("Road Trip Planner")
    
    col1, col2 = st.columns([1, 2], gap='large')  # Left column for inputs, right for results

    with col1:
        st.markdown("<h2 style='text-align: center;'>Trip Details</h2>", unsafe_allow_html=True)
        st.text("Input your trip details to calculate your optimal trip stops.")

        # User Inputs
        origin = st.text_input("Origin Address", placeholder="City, State")
        destination = st.text_input("Destination Address", placeholder="City, State")
        stop_interval = st.slider("Stop Interval (minutes)", min_value=30, max_value=120, step=15, value=90)
        car = st.text_input("Car Model", placeholder="Make Model Year (As much detail as possible)")
        locations = st.multiselect("Preferred Locations", 
                                ["Nature Spots", "Restaurants", "Historic Locations", "Rest Areas", "Playgrounds", "Zoos", "Aquariums", "Parks", "Hiking Trails", "Beaches", "National Parks", "Theme Parks", "Museums", "Children's Museums", "Botanical Gardens"],
                                placeholder="Select the type of locations you like to stop at")
        
        if st.button("Plan Trip"):
            if origin and destination:
                stops = ai.get_structured_response(f"""Origin: {origin}
                                        Destination: {destination}
                                        Stop Interval: {stop_interval} and go down 15 minutes after every stop
                                        Car: {car}
                                        Locations: {locations}
                                        """)
                            
                # Create a map
                m = folium.Map(location=[stops["stops"][2]["destination_coordinates"]["latitude"], stops["stops"][2]["destination_coordinates"]["longitude"]], 
                               zoom_start=5,
                               tiles="Cartodb dark_matter")
                for stop in stops["stops"]:
                    print(stop)
                    folium.Marker([stop["destination_coordinates"]["latitude"], stop["destination_coordinates"]["longitude"]], 
                                popup=f"{stop['stop_name']} - {stop['suggested_activity']}").add_to(m)
                
                # Save map and stops to session_state
                st.session_state["map"] = m
                st.session_state["stops"] = pd.DataFrame(stops["stops"])[["stop_name", "suggested_activity", "destination_address", "reason_for_stop"]].rename(columns={
                    "stop_name": "Stop Name",
                    "suggested_activity": "Suggested Activity",
                    "destination_address": "Destination Address",
                    "reason_for_stop": "Reason for Stop"})
            else:
                st.error("Please enter both origin and destination addresses.")

    with col2:
        if "map" in st.session_state and "stops" in st.session_state:
            st.markdown("<h2 style='text-align: center;'>Trip Map & Stops</h2>", unsafe_allow_html=True)

            col2_1, col2_2 = st.columns([1, 2], gap = "small")
            with col2_1:
                st_folium(st.session_state["map"])

            with col2_2:
                st.table(st.session_state["stops"])

if __name__ == "__main__":
    main()