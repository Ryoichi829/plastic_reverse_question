import streamlit as st
import openai
from langchain.llms import OpenAIChat
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain, SimpleSequentialChain

import os
# Streamlit Community Cloudの「Secrets」からOpenAI API keyを取得
os.environ["OPENAI_API_KEY"] = st.secrets.OpenAIAPI.openai_api_key

# LLMの初期化
llm = OpenAIChat(model="gpt-4o")

def generate_reverse_questions_chain(user_question):
    # 逆質問生成のためのプロンプトテンプレート
    reverse_question_template = PromptTemplate(
        input_variables=["question"],
        template="ユーザからの質問: {question}\nこの質問の詳細を理解するために逆質問を2つ作成してください。"
    )

    reverse_chain = LLMChain(llm=llm, prompt=reverse_question_template)
    return reverse_chain.run({"question": user_question})

def generate_final_answer_chain(user_question, reverse_questions, answers):
    # 最終回答生成のためのプロンプトテンプレート
    final_answer_template = PromptTemplate(
        input_variables=["user_question", "reverse_question1", "reverse_question2", "answer1", "answer2"],
        template=(
            "ユーザからの質問: {user_question}\n"
            "逆質問1: {reverse_question1}\n"
            "逆質問2: {reverse_question2}\n"
            "逆質問1へのユーザの回答: {answer1}\n"
            "逆質問2へのユーザの回答: {answer2}\n"
            "これらの情報を基にユーザの質問に答えてください。"
        )
    )

    final_answer_chain = LLMChain(llm=llm, prompt=final_answer_template)
    return final_answer_chain.run({
        "user_question": user_question,
        "reverse_question1": reverse_questions[0],
        "reverse_question2": reverse_questions[1],
        "answer1": answers[0],
        "answer2": answers[1]
    })


st.title("プラスチックのQAシステム")
st.write("gpt-4oを使ってます　―質問返し―")

# ユーザからの質問を入力
user_question = st.text_input("質問を入力してください:")

if user_question:
    # 逆質問を生成
    reverse_questions = generate_reverse_questions_chain(user_question).split("\n")

    if len(reverse_questions) >= 2:
        # 逆質問を表示し、ユーザの回答を取得
        reverse_answer1 = st.text_input(f"逆質問1: {reverse_questions[0]}")
        reverse_answer2 = st.text_input(f"逆質問2: {reverse_questions[1]}")

        if reverse_answer1 and reverse_answer2:
            # ユーザの回答を踏まえた最終回答を生成
            final_answer = generate_final_answer_chain(user_question, reverse_questions, [reverse_answer1, reverse_answer2])
            st.write("回答:")
            st.write(final_answer)
    else:
        st.write("逆質問を生成できませんでした。もう一度試してください。")
