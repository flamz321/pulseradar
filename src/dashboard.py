st.header("🤖 Ask PolyPulse AI")
if prompt := st.chat_input("What’s the current sentiment on..."):
    with st.spinner("Agents are analyzing live markets..."):
        report = run_pulse_crew()          # or pass user prompt dynamically
        st.markdown(report)
