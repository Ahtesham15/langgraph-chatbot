from dotenv import load_dotenv
load_dotenv()  
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph.message import add_messages



class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

llm=ChatOpenAI()

def chat_node(state: ChatState):

    #take the user query from the state
    messages=state['messages']
    #send to llm
    response=llm.invoke(messages)
    #respopnse
    return{'messages':[response]}

checkpointer = InMemorySaver() 

graph =StateGraph(ChatState)
# add nodes
graph.add_node('chat_node', chat_node)

graph.add_edge(START, 'chat_node')
graph.add_edge('chat_node',END)

chatbot=graph.compile(checkpointer=checkpointer)