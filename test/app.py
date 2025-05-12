import gradio as gr
from timetable_bot import process_input, get_timetable

def format_timetable_as_html():
    """Convert the timetable JSON into an HTML calendar-like table."""
    import json
    timetable = json.loads(get_timetable())
    if not timetable:
        return "<p>No events scheduled yet.</p>"
    
    html = "<table border='1' style='width:100%; text-align:center;'>"
    html += "<tr><th>Day</th><th>Events</th></tr>"
    
    for day, events in timetable.items():
        html += f"<tr><td>{day.capitalize()}</td><td>"
        for event in events:
            html += f"<p>{event['time']} - {event['subject']} ({event['duration']})</p>"
        html += "</td></tr>"
    
    html += "</table>"
    return html

# Gradio Interface
with gr.Blocks(title="TimeWeaver Bot") as app:
    gr.Markdown("# 🗓️ NLP Timeweaver Bot")
    
    with gr.Row():
        user_input = gr.Textbox(label="Enter your command (e.g., 'Add Math class on Monday at 10 AM for 1 hour')")
        output = gr.Textbox(label="Bot Response", interactive=False)
    
    submit_btn = gr.Button("Submit")
    submit_btn.click(fn=process_input, inputs=user_input, outputs=output)
    
    gr.Markdown("## Current Timetable")
    timetable_display = gr.HTML(value=format_timetable_as_html())
    refresh_btn = gr.Button("Refresh Timetable")
    refresh_btn.click(fn=lambda: format_timetable_as_html(), outputs=timetable_display)

app.launch()