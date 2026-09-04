from pathlib import Path
import sys
import requests
import streamlit as st
import folium
from streamlit_folium import st_folium

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ml.predict import predict_route


# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------

st.set_page_config(
    page_title="NEXORA Smart Logistics AI",
    page_icon="🚚",
    layout="wide"
)
if "route_requested" not in st.session_state:
    st.session_state.route_requested = False

st.title("🚚 NEXORA Smart Logistics Intelligence")
st.caption("AI-powered route planning • ETA prediction • Route-risk assessment")


# --------------------------------------------------
# GEOCODING
# --------------------------------------------------

@st.cache_data(ttl=3600)
def geocode_city(city):

    url = "https://nominatim.openstreetmap.org/search"

    params = {
        "q": f"{city}, India",
        "format": "jsonv2",
        "limit": 1
    }

    headers = {
        "User-Agent": "NEXORA-SIH-Prototype/1.0"
    }

    response = requests.get(
        url,
        params=params,
        headers=headers,
        timeout=10
    )

    response.raise_for_status()

    data = response.json()

    if not data:
        return None

    return {
        "lat": float(data[0]["lat"]),
        "lon": float(data[0]["lon"]),
        "name": data[0]["display_name"]
    }


# --------------------------------------------------
# ROUTING
# --------------------------------------------------

@st.cache_data(ttl=600)
def get_routes(start, end):

    url = (
        "https://router.project-osrm.org/route/v1/driving/"
        f"{start['lon']},{start['lat']};"
        f"{end['lon']},{end['lat']}"
    )

    params = {
        "alternatives": 2,
        "overview": "full",
        "geometries": "geojson"
    }

    response = requests.get(
        url,
        params=params,
        timeout=20
    )

    response.raise_for_status()

    data = response.json()

    if data.get("code") != "Ok":
        return None

    return data["routes"]


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

with st.sidebar:

    st.header("🚚 Route Planner")

    source = st.text_input(
        "From",
        placeholder="e.g. Guwahati"
    )

    destination = st.text_input(
        "To",
        placeholder="e.g. Kohima"
    )

    cargo = st.selectbox(
        "Cargo Type",
        [
            "General Goods",
            "Fragile",
            "Perishable",
            "Heavy Cargo"
        ]
    )

    priority = st.selectbox(
        "Priority",
        [
            "Fast & Safe",
            "Fastest",
            "Lowest Risk",
            "Lowest Cost"
        ]
    )

    st.divider()

    # These are temporary environmental inputs.
    # Later we can replace them with real data.

    st.subheader("Route Conditions")

    rainfall = st.slider(
        "Rainfall (mm)",
        0.0,
        180.0,
        35.0
    )

    road = st.slider(
        "Road Quality",
        1,
        5,
        3
    )

    traffic = st.slider(
        "Traffic Level",
        1,
        5,
        2
    )

    disruption = st.selectbox(
        "Known Disruption?",
        [0, 1],
        format_func=lambda x: "Yes" if x else "No"
    )

    find_route = st.button(
        "🚀 Find Best Route",
        type="primary",
        use_container_width=True
    )
    if find_route:
        st.session_state["route_requested"]=True


# --------------------------------------------------
# MAIN
# --------------------------------------------------

if st.session_state.route_requested:

    if not source or not destination:

        st.warning("Please enter both source and destination.")

        st.stop()

    # ----------------------------------------------
    # GEOCODE
    # ----------------------------------------------

    with st.spinner("Finding locations..."):

        try:

            start = geocode_city(source)
            end = geocode_city(destination)

        except Exception as e:

            st.error(f"Geocoding failed: {e}")
            st.stop()

    if start is None:

        st.error(f"Could not find '{source}'.")

        st.stop()

    if end is None:

        st.error(f"Could not find '{destination}'.")

        st.stop()


    # ----------------------------------------------
    # ROUTE
    # ----------------------------------------------

    with st.spinner("Calculating road routes..."):

        try:

            routes = get_routes(start, end)

        except Exception as e:

            st.error(f"Routing service failed: {e}")
            st.stop()

    if not routes:

        st.error("No road route could be found.")

        st.stop()


    # ----------------------------------------------
    # DISPLAY LOCATION
    # ----------------------------------------------

    st.success(
        f"Route found: **{source.title()} → {destination.title()}**"
    )


    # ----------------------------------------------
    # ROUTE DATA
    # ----------------------------------------------

    recommended = routes[0]

    distance_km = recommended["distance"] / 1000

    base_eta_hours = recommended["duration"] / 3600


    # ----------------------------------------------
    # ML PREDICTION
    # ----------------------------------------------

    # Temporary estimates for features that we don't
    # yet obtain from live environmental datasets.

    elevation = 700
    slope = 6

    x = predict_route(
        distance_km=distance_km,
        elevation_m=elevation,
        slope_pct=slope,
        rainfall_mm=rainfall,
        road_quality=road,
        traffic_level=traffic,
        disruption=disruption
    )


    # ----------------------------------------------
    # KPI CARDS
    # ----------------------------------------------

    st.subheader("⭐ NEXORA Recommendation")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Distance",
        f"{distance_km:.1f} km"
    )

    col2.metric(
        "Base ETA",
        f"{base_eta_hours:.1f} hr"
    )

    col3.metric(
        "AI ETA",
        f"{x['eta_hours']:.1f} hr"
    )

    col4.metric(
        "Risk",
        x["risk"]
    )


    # ----------------------------------------------
    # RISK MESSAGE
    # ----------------------------------------------

    if x["risk"] == "High":

        st.error(
            "⚠️ High-risk route — NEXORA recommends evaluating an alternative."
        )

    elif x["risk"] == "Medium":

        st.warning(
            "⚠️ Medium-risk route — monitor route conditions."
        )

    else:

        st.success(
            "✅ Low-risk route — recommended."
        )


    # ----------------------------------------------
    # MAP
    # ----------------------------------------------

    st.subheader("🗺️ Recommended Route")

    route_coords = [
        [point[1], point[0]]
        for point in recommended["geometry"]["coordinates"]
    ]

    center_lat = (start["lat"] + end["lat"]) / 2
    center_lon = (start["lon"] + end["lon"]) / 2

    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=7
    )

    folium.Marker(
        [start["lat"], start["lon"]],
        tooltip=f"Start: {source.title()}",
        icon=folium.Icon(color="green")
    ).add_to(m)

    folium.Marker(
        [end["lat"], end["lon"]],
        tooltip=f"Destination: {destination.title()}",
        icon=folium.Icon(color="red")
    ).add_to(m)

    folium.PolyLine(
        route_coords,
        weight=6,
        tooltip="NEXORA Recommended Route"
    ).add_to(m)


    # Alternative route

    if len(routes) > 1:

        alternative = routes[1]

        alternative_coords = [
            [point[1], point[0]]
            for point in alternative["geometry"]["coordinates"]
        ]

        folium.PolyLine(
            alternative_coords,
            weight=4,
            dash_array="10",
            tooltip="Alternative Route"
        ).add_to(m)


    st_folium(
        m,
        use_container_width=True,
        height=500
    )


    # ----------------------------------------------
    # ROUTE COMPARISON
    # ----------------------------------------------

    st.subheader("📊 Route Comparison")

    comparison = []

    for i, route in enumerate(routes):

        route_distance = route["distance"] / 1000
        route_eta = route["duration"] / 3600

        comparison.append(
            {
                "Route":
                    "⭐ Recommended"
                    if i == 0
                    else f"Alternative {i}",

                "Distance (km)":
                    round(route_distance, 1),

                "Base ETA (hr)":
                    round(route_eta, 2)
            }
        )

    st.dataframe(
        comparison,
        use_container_width=True,
        hide_index=True
    )


    # ----------------------------------------------
    # RISK FACTORS
    # ----------------------------------------------

    st.subheader("⚠️ Risk Factors")

    reasons = []

    if rainfall >= 70:
        reasons.append("High rainfall")

    if road <= 2:
        reasons.append("Poor road quality")

    if traffic >= 4:
        reasons.append("Heavy traffic")

    if disruption:
        reasons.append("Known disruption")

    if reasons:

        for reason in reasons:
            st.write(f"• {reason}")

    else:

        st.write("No major demo risk thresholds crossed.")


else:

    st.info(
        "Enter a source and destination in the sidebar "
        "and click **Find Best Route**."
    )


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()

st.caption(
    "NEXORA pipeline: Location → Routing → ML → ETA + Risk → Recommendation"
)