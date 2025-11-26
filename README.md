# **Technical Support Customer Chatbot**

<img width="1046" height="613" alt="image" src="https://github.com/user-attachments/assets/cf1eb356-5ecf-4717-9612-e5c474e92875" />The above is the workflow of the project

---

# 🚀 **Setup & Running Guide**

This project is an AI-powered customer-support system that uses **FastAPI + LLaMA (Ollama)** to behave like a human support agent.
It understands user intent, extracts sales lead info, stores feature requests, and replies naturally.

---

# ✅ **1. Prerequisites**

Make sure you have the following installed:

### **✔ Python 3.10+**

### **✔ pip**

### **✔ Ollama (for running LLaMA models locally)**

Download from: [https://ollama.com/download](https://ollama.com/download)

---

# ✅ **2. Install Dependencies**

Inside your project folder:

```bash
python -m venv .venv
```

Activate the virtual environment:

### **Windows**

```bash
.venv\Scripts\activate
```

### **Mac/Linux**

```bash
source .venv/bin/activate
```

Then install requirements:

```bash
pip install -r requirements.txt
```

---

# ✅ **3. Pull the Required Model**

This project uses **LLaMA 3.2** (or any local model).

```bash
ollama pull llama3.2
```

Test it:

```bash
ollama run llama3.2 "hello"
```

You should get a response.
If yes → your model is working.

---

# ✅ **4. Start Ollama Server**

Before running FastAPI, Ollama **must** be running:

```bash
ollama serve
```

Leave this terminal open.

---

# ✅ **5. Start the API Server**

Open a new terminal inside the project folder:

```bash
uvicorn api:app --reload --port 8000
```

You should see:

```
Uvicorn running on http://127.0.0.1:8000
Application startup complete.
```

---

# ✅ **6. Testing the API (Postman / curl / frontend)**

Send a POST request to:

```
POST http://127.0.0.1:8000/chat
```

JSON body:

```json
{
  "message": "Hi, I am interested in your product",
  "session_id": "test123"
}
```

You will get a human-like reply and the system will:

* classify intent
* store missing sales fields
* save feature requests
* pull responses from KB if technical
* behave like a human agent

---

# 📁 **7. Data Storage Locations**

### **Sales leads**

Stored automatically in:

```
/leads/<session_id>.json
```

### **Feature requests**

Stored in:

```
/feature_requests/<session_id>.txt
```

### **Knowledge Base files (for KB search)**

Stored in:

```
/kb/
```

---

# 🎯 **8. Stop Servers**

### Stop FastAPI:

Press

```
CTRL + C
```

### Stop Ollama:

```bash
taskkill /F /IM ollama.exe   # Windows
```

or

```bash
pkill ollama     # Mac/Linux
```

---

# 🎉 You’re Ready to Use the System

This setup gives you a **fully functional intelligent support agent**, running completely on your machine, offline, and storing session memory locally.

If you want a **fully polished README plus images, badges, diagrams**, just ask!
