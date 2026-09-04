from pathlib import Path
import sys, streamlit as st
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT))
from ml.predict import predict_route

st.set_page_config(page_title="NER Smart Logistics AI",page_icon="🚚",layout="wide")
st.title("🚚 NER Smart Logistics & Accessibility Intelligence")
st.caption("SIH prototype • ETA + route-risk prediction")
st.info("Demo only: the included dataset is synthetic , only for demonstration purposes.")

with st.sidebar:
    st.header("Route conditions")
    distance=st.slider("Distance (km)",5.,500.,120.)
    elevation=st.slider("Elevation (m)",0.,2200.,700.)
    slope=st.slider("Average slope (%)",0.,18.,6.)
    rainfall=st.slider("Rainfall (mm)",0.,180.,35.)
    road=st.slider("Road quality",1,5,3)
    traffic=st.slider("Traffic level",1,5,2)
    disruption=st.selectbox("Known disruption?",[0,1],format_func=lambda x:"Yes" if x else "No")
    go=st.button("Predict Route",type="primary")

st.subheader("AI Recommendation")
if go:
    x=predict_route(distance_km=distance,elevation_m=elevation,slope_pct=slope,rainfall_mm=rainfall,
                    road_quality=road,traffic_level=traffic,disruption=disruption)
    a,b,c=st.columns(3); a.metric("Predicted ETA",f"{x['eta_hours']} hr"); b.metric("Risk",x["risk"]); c.metric("Confidence",f"{x['confidence']*100:.0f}%")
    if x["risk"]=="High": st.error("⚠️ High risk — consider an alternative route.")
    elif x["risk"]=="Medium": st.warning("⚠️ Medium risk — monitor conditions.")
    else: st.success("✅ Low-risk route.")
    reasons=[]
    if rainfall>=70: reasons.append("High rainfall")
    if slope>=10: reasons.append("Steep terrain")
    if road<=2: reasons.append("Poor road quality")
    if traffic>=4: reasons.append("Heavy traffic")
    if disruption: reasons.append("Known disruption")
    st.write("### Risk factors")
    st.write("\n".join("• "+r for r in reasons) if reasons else "No major demo thresholds crossed.")
    st.write("### Route comparison")
    st.dataframe([
        {"Route":"Recommended","ETA (hr)":x["eta_hours"],"Risk":x["risk"]},
        {"Route":"Alternative A","ETA (hr)":round(x["eta_hours"]*1.10,2),"Risk":"Low" if x["risk"]=="High" else "Medium"},
        {"Route":"Alternative B","ETA (hr)":round(x["eta_hours"]*1.22,2),"Risk":"Low"}],
        use_container_width=True,hide_index=True)
else:
    st.write("Choose conditions in the sidebar and click Predict Route.")

st.divider()
st.code("Route data → ML → ETA + Risk → Route recommendation → Dashboard")
