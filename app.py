import gradio as gr
from llm_client import query_llm

def chat(user_input):
    return query_llm(user_input)

demo = gr.Interface(
    fn=chat,
    inputs=gr.Textbox(label="Afaan Oromoo Input", placeholder="Gaaffii keessan asitti barreessaa..."),
    outputs=gr.Textbox(label="AI Response"),
    title="Afaan Oromoo AI (Gemini Flash)",
    description="Powered by Google Gemini 1.5 Flash (VPN Required)"
)

if __name__ == "__main__":
    demo.launch()