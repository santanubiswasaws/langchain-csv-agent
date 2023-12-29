#from langchain.agents import create_csv_agent
from langchain_experimental.agents import create_csv_agent
from langchain.llms import OpenAI
from dotenv import load_dotenv
import os
import streamlit as st
import pandas as pd 


def main():
    load_dotenv()

    # Load the OpenAI API key from the environment variable
    if os.getenv("OPENAI_API_KEY") is None or os.getenv("OPENAI_API_KEY") == "":
        print("OPENAI_API_KEY is not set")
        exit(1)
    else:
        print("OPENAI_API_KEY is set")

    st.set_page_config(page_title="Ask your CSV", layout='wide')
    st.header("Ask your CSV 📈")

    csv_file = st.file_uploader("Upload a CSV file", type="csv")
    if csv_file is not None:
        try:
            st_df = pd.read_csv(csv_file, delimiter=',')
            #
            # reset the file pointer to the begining of the file - for agent code to read it - to avoid 
            # pandas.errors.EmptyDataError: No columns to parse from file - errror 
            csv_file.seek(0)
        except pd.errors.EmptyDataError:
            # Handle empty file case
            print("The file is empty.")

        # Pivot the DataFrame
        st_df_pivot = st_df.pivot(index='CUSTOMER_ID', columns='MONTH', values= 'MONTHLY_REVENUE').round(2)

        # 
        row_totals = st_df_pivot.sum(axis=1)

        # Add the row totals as the first column
        st_df_pivot.insert(0, 'Customer_Totals', row_totals)

        column_totals = st_df_pivot.sum(axis=0)

        # Create a new DataFrame with the column totals
        totals_df = pd.DataFrame(column_totals.values.reshape(1, -1), columns=st_df_pivot.columns, index=['Totals'])

        # Concatenate the original DataFrame with the totals DataFrame
        st_df_pivoted_with_totals = pd.concat([st_df_pivot, totals_df])



        # st.dataframe(st_df, use_container_width=True, hide_index=True, height=220)
        st.dataframe(st_df, hide_index=True, height=220)
        st.dataframe(st_df_pivoted_with_totals, use_container_width=True)


        agent = create_csv_agent(
            OpenAI(temperature=0), csv_file, verbose=True)

        user_question = st.text_input("Ask a question about your CSV: ")

        if user_question is not None and user_question != "":
            with st.spinner(text="In progress..."):
                answer=agent.run(user_question)
                #st.write(agent.run(user_question))
                #print(answer)
                st.write(answer)
            



if __name__ == "__main__":
    main()
