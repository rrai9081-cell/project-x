import streamlit as st
import pandas as pd
from datetime import datetime, date

# --- Page Config ---
st.set_page_config(
    page_title="Career Dashboard - MSc Financial Analytics",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- State Management ---
if 'jobs' not in st.session_state:
    st.session_state.jobs = [
        # Part-time
        {"ID": 1, "Tab": "Part-time", "Company": "QUB Campus", "Role": "Student Assistant", "Deadline": date(2026, 9, 15), "Status": "Tracking", "Country": ""},
        {"ID": 2, "Tab": "Part-time", "Company": "Retail/Hospitality", "Role": "Customer Service", "Deadline": date(2026, 9, 20), "Status": "Applied", "Country": ""},
        {"ID": 3, "Tab": "Part-time", "Company": "Reed/Hays/Robert Half", "Role": "Finance Admin", "Deadline": date(2026, 10, 1), "Status": "Tracking", "Country": ""},
        
        # Internships
        {"ID": 4, "Tab": "Internships", "Company": "Citi Belfast", "Role": "Placement Analyst", "Deadline": date(2027, 2, 15), "Status": "Tracking", "Country": ""},
        {"ID": 5, "Tab": "Internships", "Company": "EY", "Role": "Corporate Finance", "Deadline": date(2027, 2, 28), "Status": "Tracking", "Country": ""},
        {"ID": 6, "Tab": "Internships", "Company": "FD Technologies", "Role": "Data Analyst", "Deadline": date(2027, 3, 1), "Status": "Tracking", "Country": ""},
        {"ID": 7, "Tab": "Internships", "Company": "Davy Group", "Role": "Wealth Management", "Deadline": date(2027, 3, 10), "Status": "Tracking", "Country": ""},

        # Europe Grad Roles
        {"ID": 8, "Tab": "Europe", "Company": "Deutsche Bank", "Role": "Finance Analyst", "Country": "Germany", "Deadline": date(2026, 10, 31), "Status": "Tracking"},
        {"ID": 9, "Tab": "Europe", "Company": "ING", "Role": "Risk Trainee", "Country": "Netherlands", "Deadline": date(2026, 11, 15), "Status": "Tracking"},
        {"ID": 10, "Tab": "Europe", "Company": "Clearstream/BNP", "Role": "Fund Admin", "Country": "Luxembourg", "Deadline": date(2026, 11, 30), "Status": "Tracking"},
        {"ID": 11, "Tab": "Europe", "Company": "Bank of Ireland", "Role": "Grad Prog", "Country": "Dublin (No Visa)", "Deadline": date(2026, 10, 15), "Status": "Tracking"},
    ]

# --- Helper Functions ---
def add_job(tab_name, company, role, deadline, status, country=""):
    new_id = max([job["ID"] for job in st.session_state.jobs] + [0]) + 1
    st.session_state.jobs.append({
        "ID": new_id,
        "Tab": tab_name,
        "Company": company,
        "Role": role,
        "Deadline": deadline,
        "Status": status,
        "Country": country
    })

def render_tracker(tab_name, has_country=False):
    # Filter data for this tab
    df = pd.DataFrame([j for j in st.session_state.jobs if j["Tab"] == tab_name])
    
    if df.empty:
        st.info("No entries found. Add one below!")
    else:
        # Columns to display
        display_cols = ["Company", "Role", "Country", "Deadline", "Status"] if has_country else ["Company", "Role", "Deadline", "Status"]
        
        # Display editable dataframe (we sync changes back to session_state)
        edited_df = st.data_editor(
            df[display_cols],
            use_container_width=True,
            hide_index=True,
            column_config={
                "Deadline": st.column_config.DateColumn("Deadline"),
                "Status": st.column_config.SelectboxColumn("Status", options=["Tracking", "Applied", "Interview", "Offer"]),
            }
        )
        # Note: In a fully productionized app, we'd sync the edited_df back to st.session_state.jobs

    st.markdown("### Add New Entry")
    with st.form(f"form_{tab_name}", clear_on_submit=True):
        col1, col2 = st.columns(2)
        company = col1.text_input("Company")
        role = col2.text_input("Role")
        
        country = ""
        if has_country:
            country = st.text_input("Country")
            
        col3, col4 = st.columns(2)
        deadline = col3.date_input("Deadline")
        status = col4.selectbox("Status", ["Tracking", "Applied", "Interview", "Offer"])
        
        submitted = st.form_submit_button("Add to Tracker")
        if submitted and company and role:
            add_job(tab_name, company, role, deadline, status, country)
            st.rerun()

# --- Header ---
st.title("🎓 Raj Vardhan Kumar | Career Dashboard")
st.markdown("MSc Financial Analytics @ Queen's University Belfast")

# --- Tabs ---
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Overview", 
    "💼 Part-time Jobs", 
    "🏫 QUB Internships", 
    "🌍 Europe Grad Roles", 
    "📅 Timeline"
])

# --- 1. Overview Tab ---
with tab1:
    st.warning("**⚠️ Visa Work Hours Limit:** International students on a Student Visa are strictly limited to working a maximum of **20 hours per week** during term time.")
    
    col1, col2, col3, col4 = st.columns(4)
    
    total_applied = len([j for j in st.session_state.jobs if j["Status"] in ["Applied", "Interview", "Offer"]])
    total_tracking = len(st.session_state.jobs)
    
    target_date = date(2026, 9, 1)
    days_left = max(0, (target_date - date.today()).days)
    
    col1.metric("Total Applications", total_applied)
    col2.metric("Roles Tracking", total_tracking)
    col3.metric("Days Until Sept 2026", days_left)
    col4.metric("Max Work Hrs / Week", "20")
    
    st.markdown("### 🔗 Quick Links")
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.link_button("QUB MyFuture", "https://qub-csm.symplicity.com/students/", use_container_width=True)
    c2.link_button("Citi Belfast Jobs", "https://jobs.citi.com/belfast", use_container_width=True)
    c3.link_button("NIJobs", "https://www.nijobs.com/", use_container_width=True)
    c4.link_button("LinkedIn", "https://www.linkedin.com/jobs/", use_container_width=True)
    c5.link_button("EURES (Europe)", "https://eures.ec.europa.eu/", use_container_width=True)
    c6.link_button("Indeed Belfast", "https://uk.indeed.com/jobs-in-Belfast", use_container_width=True)

# --- 2. Part-time Jobs Tab ---
with tab2:
    st.subheader("Belfast Part-Time Job Tracker")
    st.info("💡 Focus: QUB campus roles, retail, hospitality, and finance admin via Reed/Hays/Robert Half.")
    render_tracker("Part-time")

# --- 3. QUB Internships Tab ---
with tab3:
    st.subheader("QUB Internships Tracker")
    st.info("💡 Tip: Use prefix 'QUBINTERN' on MyFuture. Most internships open around February 2027.")
    render_tracker("Internships")

# --- 4. Europe Grad Roles Tab ---
with tab4:
    st.subheader("Europe Grad Roles Tracker")
    st.info("💡 Note: Target dates are Oct-Nov 2026 for 2027 entry. Focus on visa-friendly routes.")
    render_tracker("Europe", has_country=True)

# --- 5. Timeline Tab ---
with tab5:
    st.subheader("Action Plan Timeline")
    
    st.markdown("""
    **🟢 Now → September 2026: Arrival & Setup**
    * Enrol in MSc Financial Analytics at Queen's University Belfast.
    * Activate QUB MyFuture account.
    * Begin immediate search for part-time jobs (max 20hrs/week) via campus roles or local agencies (Reed, Hays).
    
    **🟢 October 2026 – November 2026: European Grad Cycles Open**
    * Major European banks and financial institutions open their 2027 graduate programs.
    * Start applying to target countries with favorable visa routes: Ireland (Dublin - no visa needed), Germany (job-seeker visa), Netherlands (orientation visa), Luxembourg.
    
    **🟢 February 2027: QUB Internships Search**
    * QUBINTERN roles open on MyFuture.
    * Apply aggressively for summer placements and internships in Belfast (e.g., Citi, EY, FD Technologies, Davy Group).
    
    **🟢 Summer 2027: Internship Execution**
    * Complete summer internship/placement.
    * Focus on securing a return offer or building strong local references for the post-grad job hunt.
    
    **🟢 Post-Graduation (Late 2027): Full-time Transition**
    * Transition to Graduate visa routes (UK 2-year Graduate Route or EU Job-Seeker visas).
    * Begin full-time employment.
    """)
