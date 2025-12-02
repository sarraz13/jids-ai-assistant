from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser


# 1) LLM
model = ChatOpenAI(model="gpt-4o-mini")

# 2) Prompt
prompt = PromptTemplate.from_template(
    "Answer the following question in one sentence: {question}"
)

# 3) Chain (new syntax)
chain = prompt | model | StrOutputParser()

# 4) Run
response = chain.invoke({"question": "What is Django?"})
print("AI Response:", response)
