from fastapi import FastAPI

from db_agent import query_db_with_natural_language
from invoice_routes import router as invoice_routes
from user_routes import router as user_router
from agent_routes import router as agent_routes
import gradio as gr
from uuid import uuid4


app = FastAPI(
    title="CClarke ORM Implementation with DB Agent",
)

def db_agent_gradio_ui():
    with gr.Blocks() as db_ui:
        gr.Markdown("# CClarke ORM Implementation with DB Agent")
        gr.Markdown("Ask questions from your database with natural language")

        thread_id = gr.State(str(uuid4()))
        chatbot = gr.Chatbot(label="Conversation")
        msg = gr.Textbox(label="Enter your message")

        def respond(message : str , history : list , current_thread_id : str):
            result = query_db_with_natural_language(message , thread_id=current_thread_id)

            history = history + [
                {"role" : "user" , "content" : message},
                {"role" : "assistant" , "content" : result}
            ]
            return history , "" , current_thread_id

        msg.submit(
            respond,
            inputs=[msg , chatbot , thread_id],
            outputs=[chatbot , msg , thread_id],
        )

    return db_ui

app = gr.mount_gradio_app(app , db_agent_gradio_ui() , path="/agent/ui")


app.include_router(user_router)
app.include_router(invoice_routes)
app.include_router(agent_routes)