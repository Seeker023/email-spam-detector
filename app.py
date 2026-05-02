import gradio as gr
from src.predict import predict_spam

def classify_email(email_text):
    if not email_text.strip():
        return "Please enter some text.", "N/A"
        
    try:
        label, confidence = predict_spam(email_text)
        return label, f"{confidence}%"
    except Exception as e:
        return f"Error: {str(e)}", "N/A"

# Build Gradio interface
with gr.Blocks(title="Email Spam Detector", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 📧 Email Spam Detection System")
    gr.Markdown("Paste the content of an email below to determine if it is **Spam** or **Ham** (Not Spam).")
    
    with gr.Row():
        with gr.Column(scale=2):
            input_text = gr.Textbox(
                lines=10, 
                placeholder="Paste email text here...", 
                label="Email Content"
            )
            submit_btn = gr.Button("Analyze Email", variant="primary")
            
        with gr.Column(scale=1):
            output_label = gr.Textbox(label="Prediction (Spam/Ham)", text_align="center")
            output_conf = gr.Textbox(label="Confidence Score", text_align="center")
            
    submit_btn.click(
        fn=classify_email, 
        inputs=input_text, 
        outputs=[output_label, output_conf]
    )
    
    gr.Examples(
        examples=[
            ["URGENT: Your bank account has been suspended. Please click the link to verify your identity."],
            ["Hi Team, Just a reminder that our weekly sync is scheduled for 10 AM tomorrow in the main conference room."],
            ["Claim your free iPhone 15 now! Limited time offer, act fast!"],
        ],
        inputs=input_text
    )

if __name__ == "__main__":
    demo.launch(share=False)
