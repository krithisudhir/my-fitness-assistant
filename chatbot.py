

import os.path
import requests
from taipy.gui import Gui, State, notify

from llama_index.core import ( # type: ignore
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
    load_index_from_storage,
)

context = "The following is a conversation with my personal fitness AI assistant. The assistant is helpful, knowledgeable and friendly.\n\nHuman: Hello, who are you?\nAI: I am Krithi's AI assistant. How can I help you today? "
conversation = {
    "Conversation": ["Who are you?", "Hi! I am a fine-tuned GPT Turbo 3.5. How can I help you today?"]
}
current_user_message = ""

def request(state: State, prompt: str) -> str:
    """
    Send a prompt to the HuggingFace API and return the response.

    Args:
        - state: The current state of the app.
        - prompt: The prompt to send to the API.

    Returns:
        The response from the API.
    """
    # check if storage already exists
    PERSIST_DIR = "./storage"
    if not os.path.exists(PERSIST_DIR):
        # load the documents and create the index
        documents = SimpleDirectoryReader("data").load_data()
        index = VectorStoreIndex.from_documents(documents)
        # store it for later
        index.storage_context.persist(persist_dir=PERSIST_DIR)
    else:
        # load the existing index
        storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
        index = load_index_from_storage(storage_context)
        query_engine = index.as_query_engine()
        response = query_engine.query(
            {
                "inputs": prompt,
            }
        )
        print(response)
        output= response[0]["generated_text"]
        return output.json()


def send_message(state: State) -> None:
    """
    Send the user's message to the API and update the conversation.

    Args:
        - state: The current state of the app.
    """
    # Add the user's message to the context
    state.context += f"Human: \n {state.current_user_message}\n\n AI:"
    # Send the user's message to the API and get the response
    answer = request(state, state.context).replace("\n", "")
    # Add the response to the context for future messages
    state.context += answer
    # Update the conversation
    conv = state.conversation._dict.copy()
    conv["Conversation"] += [state.current_user_message, answer]
    state.conversation = conv
    # Clear the input field
    state.current_user_message = ""


page = """
<|{conversation}|table|show_all|width=100%|>
<|{current_user_message}|input|label=Write your message here...|on_action=send_message|class_name=fullwidth|>
"""
if __name__ == "__main__":
    Gui(page).run(dark_mode=True, title="Taipy Chat")
