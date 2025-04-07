import streamlit as st
import requests

# Mapping for test type letters to full names and descriptions
test_type_info = {
    "A": "Ability & Aptitude",
    "B": "Biodata & Situational Judgement",
    "C": "Competencies",
    "D": "Development & 360",
    "E": "Assessment Exercises",
    "K": "Knowledge & Skills",
    "P": "Personality & Behavior",
    "S": "Simulations"
}

# Tooltip style and formatting
tooltip_style = """
<style>
.tooltip-box {
    display: inline-block;
    background-color: #2e2f38;
    color: white;
    padding: 4px 8px;
    font-weight: bold;
    border-radius: 4px;
    border: 1px solid white;
    position: relative;
    margin-right: 5px;
    font-family: sans-serif;
}
.tooltip-box:hover::after {
    content: attr(data-tooltip);
    position: absolute;
    background: #333;
    color: #fff;
    padding: 6px 10px;
    border-radius: 6px;
    top: 120%;
    left: 0;
    white-space: nowrap;
    z-index: 10;
    font-size: 12px;
    box-shadow: 0px 0px 10px rgba(0,0,0,0.4);
}
</style>
"""

# Set Streamlit page config
st.set_page_config(page_title="SHL Assessment Recommender", layout="wide")
st.markdown(tooltip_style, unsafe_allow_html=True)


st.title("🔍 SHL Assessment Recommender")

# Text area for user input
query = st.text_area("Enter job description or requirement:")

# On button click, send query to backend
if st.button("Get Recommendations"):
    if not query.strip():
        st.warning("Please enter a job description.")
    else:
        try:
            response = requests.post(
                "https://shl-recommender-xrg0.onrender.com",
                json={"query": query}
            )

            if response.status_code == 200:
                data = response.json()
                recommendations = data.get("recommendations", [])

                if not recommendations:
                    st.info("No recommendations found.")
                else:
                    st.subheader("Top Recommended Assessments")

                    table_md = """
<table>
<thead>
<tr>
<th>#</th>
<th>Assessment</th>
<th>Link</th>
<th>Remote</th>
<th>Adaptive</th>
<th>Test Type</th>
<th>Duration(in min)</th>
</tr>
</thead>
<tbody>
"""

                    for idx, item in enumerate(recommendations, 1):
                        # Build the tooltip HTML for test types
                        types = item["Test Type"].replace(" ", "").split(",")
                        test_type_html = ""
                        for t in types:
                            t = t.upper()
                            if t in test_type_info:
                                test_type_html += f'<span class="tooltip-box" data-tooltip="{test_type_info[t]}">{t}</span>'
                            else:
                                test_type_html += f'<span class="tooltip-box" data-tooltip="Unknown">{t}</span>'

                        table_md += f"""
<tr>
<td>{idx}</td>
<td>{item['Assessment Name']}</td>
<td><a href="{item['URL']}" target="_blank">Link for Test</a></td>
<td>{item['Remote Testing']}</td>
<td>{item['Adaptive/IRT']}</td>
<td>{test_type_html}</td>
<td>{item['Duration']}</td>
</tr>
"""

                    table_md += "</tbody></table>"

                    st.markdown(table_md, unsafe_allow_html=True)

            else:
                st.error("❌ Failed to get recommendations from the backend.")
        except Exception as e:
            st.error(f"❌ An error occurred: {str(e)}")
