import streamlit as st
from dotenv import load_dotenv
from fpl_agent.backend.agent.sql_agent import Agent

load_dotenv()


st.set_page_config(page_title="I can Retrieve Any SQL query")
st.header("Gemini App To Retrieve SQL Data")

agent = Agent()
question = st.text_input("Input: ", key="input")
submit = st.button("Ask the question")

# if submit is clicked
if submit:
    response = agent.get_gemini_response(question=question)
    result = agent.read_sql_query(response)
    # clean_response = response.replace("```", "")
    # if clean_response.startswith("sql"):
    #     clean_response = clean_response.replace("sql", "")
    # data = agent.read_sql_query(clean_response)
    st.subheader("The response is:")
    st.header(result)
    st.text("Data line-by-line:")
    for row in result:
        print(row)
        st.header(row)

if __name__ == "__main__":
    agent = Agent()
