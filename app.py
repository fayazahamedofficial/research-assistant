import streamlit as st
from src.pipeline import research_from_urls
from src.report import to_markdown

st.set_page_config(page_title="ResearchLens", page_icon="🔎")
st.title("🔎 ResearchLens")
st.caption("Paste URLs and get a structured, cited research report.")

urls_text = st.text_area(
    "URLs (one per line)", height=120,
    placeholder="https://en.wikipedia.org/wiki/Honey_bee",
)
depth = st.radio("Depth", ["Quick", "Detailed"], horizontal=True)
MAX_CHUNKS = {"Quick": 2, "Detailed": 6}   # fewer chunks = fewer API calls

if st.button("Generate report", type="primary"):
    urls = [u.strip() for u in urls_text.splitlines() if u.strip()]
    if not urls:
        st.warning("Please enter at least one URL.")
    else:
        with st.spinner("Reading pages and writing the report. This can take a minute on the free tier..."):
            try:
                report, errors = research_from_urls(urls, max_chunks=MAX_CHUNKS[depth])
            except Exception as e:
                st.error(f"Something went wrong: {e}")
                st.stop()
        # Keep the result, because Streamlit re-runs this whole file on every click
        st.session_state["report"] = report
        st.session_state["errors"] = errors

if "report" in st.session_state:
    report = st.session_state["report"]
    for err in st.session_state["errors"]:
        st.warning(err[:200])

    st.header(report.title)
    st.write(report.summary)

    st.subheader("Key points")
    for kp in report.key_points:
        refs = " ".join(f"[{i}]" for i in kp.source_ids)
        st.markdown(f"- {kp.point} **{refs}**")

    st.subheader("Open questions")
    for q in report.open_questions:
        st.markdown(f"- {q}")

    st.subheader("Sources")
    for s in report.sources:
        st.markdown(f"{s.id}. [{s.title}]({s.url})")

    st.download_button(
        "Download as Markdown", to_markdown(report),
        file_name="report.md", mime="text/markdown",
    )