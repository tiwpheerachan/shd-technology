# 🔹 Base image
FROM python:3.10.13-slim

# 🔹 Set working directory
WORKDIR /app

# 🔹 Install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# 🔹 Copy app
COPY . .

# 🔹 Expose Streamlit default port
EXPOSE 8501

# 🔹 Run the app
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
