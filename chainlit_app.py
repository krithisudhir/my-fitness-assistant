import chainlit as cl
import os.path
from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
    load_index_from_storage
)
from llama_index.llms.openai import OpenAI 
PERSIST_DIR = "./storage"

if not os.path.exists(PERSIST_DIR):
    # load the documents and create the index
    documents = SimpleDirectoryReader("data").load_data()
    index = VectorStoreIndex.from_documents(documents)
    # store it for later
    index.storage_context.persist(persist_dir=PERSIST_DIR)
else:
    # load  existing index
    storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
    index = load_index_from_storage(storage_context)

llm = OpenAI(model="gpt-3.5-turbo-0613")
# docs = SimpleDirectoryReader("data").load_data()
# index = VectorStoreIndex.from_documents(docs)
chat_engine = index.as_chat_engine(chat_mode="openai", llm=llm, verbose=True)
prompts=[{"role":"system","content":"You are an AI assistant who is knowledgeable and friendly."}]

@cl.on_message
async def main(prompt: cl.Message):
    prompts.append({"role":"user","content":prompt.content})
    #query_engine = index.as_query_engine(chainl)
    response = chat_engine.chat(prompt.content, tool_choice="query_engine_tool")
    prompts.append({"role":"assistant","content":response})

    # Send a response back to the user
    await cl.Message(
        content=response
    ).send()



