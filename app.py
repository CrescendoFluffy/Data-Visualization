from flask import Flask, render_template, request, redirect, url_for
import os
import pandas as pd
import plotly.express as px
import plotly
import json

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        if file:
            filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filename)
            return redirect(url_for('visualize', filename=file.filename))
    return render_template('upload.html')

@app.route('/visualize/<filename>')
def visualize(filename):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    try:
        df = pd.read_csv(filepath)

        # Ensure the CSV has at least two columns
        if len(df.columns) >= 2:
            x_col = df.columns[0]
            y_col = df.columns[1]

            # Line Chart
            line_fig = px.line(df, x=x_col, y=y_col, title="Financial Trend Analysis")
            line_graphJSON = json.dumps(line_fig, cls=plotly.utils.PlotlyJSONEncoder)

            # Bar Chart
            bar_fig = px.bar(df, x=x_col, y=y_col, title="Comparative Bar Chart")
            bar_graphJSON = json.dumps(bar_fig, cls=plotly.utils.PlotlyJSONEncoder)

            # Histogram
            hist_fig = px.histogram(df, x=y_col, title="Histogram of Financial Data")
            hist_graphJSON = json.dumps(hist_fig, cls=plotly.utils.PlotlyJSONEncoder)

            # Pie Chart (uses the second column as values)
            pie_fig = px.pie(df, names=x_col, values=y_col, title="Pie Chart of Financial Data")
            pie_graphJSON = json.dumps(pie_fig, cls=plotly.utils.PlotlyJSONEncoder)

            return render_template(
                'visualization_plotly.html',
                line_graphJSON=line_graphJSON,
                bar_graphJSON=bar_graphJSON,
                hist_graphJSON=hist_graphJSON,
                pie_graphJSON=pie_graphJSON,
                filename=filename
            )
        else:
            return "CSV needs at least two columns for financial visualization.", 400
    except Exception as e:
        return f"Error processing file: {str(e)}", 500

if __name__ == '__main__':
    app.run(debug=True)
