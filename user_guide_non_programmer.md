# Beginner's Guide: How to Run & Use the Research Orchestrator

> **No coding experience required!** This simple guide will walk you through launching, checking, and asking research questions on the **Stateful Multi-Agent Research Orchestrator**.

---

## 🚀 Quick Check: Try It Right Now!

The application is **currently running live** on your computer. You can check it immediately in 2 easy steps:

1. Open your web browser (Google Chrome, Microsoft Edge, Mozilla Firefox, or Safari).
2. Click or type this web link into your browser address bar:
   👉 **`http://localhost:3000`**

You will see the **JRC Automotive Data Research** dashboard!

---

## 🚗 What Does This Application Do?

Imagine you have a team of 4 AI assistants working together to answer complex questions about European cars, electric vehicles (EVs), fuel consumption, emissions, and autonomous driving:

1. **🧠 The Planner**: Reads your question and breaks it down into 3-4 specific sub-topics.
2. **🔎 The Searcher (Retriever)**: Searches through thousands of official European Commission JRC research papers to find real scientific data.
3. **✍️ The Writer (Synthesiser)**: Combines all the findings into a clear, structured report with official citations.
4. **🔍 The Inspector (Validator)**: Checks the writer's work. If anything is missing, it sends the searcher back to get the missing information before giving you the final answer!

---

## 🖥️ How to Use the Web Dashboard

### Step 1: Pick or Type a Question
- **Option A (One-Click Examples)**: Click any of the blue sample question buttons at the top:
  - *“How does cold weather affect real-world EV range?”*
  - *“What is the gap between WLTP and real-world fuel consumption for PHEVs?”*
  - *“What does JRC data show about real-world CO2 emissions under RDE conditions?”*
- **Option B (Custom Query)**: Type your own question into the text box.

### Step 2: (Optional) Apply Filters
- Use the dropdown menus below the text box to filter research by:
  - **Category**: Electric Vehicles (BEV), Plug-In Hybrids (PHEV), Emissions (RDE), Hydrogen & Heavy Duty, or Autonomous ADAS.
  - **Publication Year**: 2024 or 2023.

### Step 3: Launch Research
- Click the purple **“Launch Graph Research ⚡”** button (or press `Ctrl + Enter` on your keyboard).

### Step 4: Read Your Results
The screen will display 4 cards:
1. **🔄 Status Badge**: Shows if your answer passed inspection immediately or required a 2nd search pass.
2. **🧠 Agent Execution Trace**: Displays a step-by-step visual timeline showing how each AI node worked.
3. **✍️ Synthesised Evidence Report**: The final structured research answer citing official JRC data.
4. **📄 Document Provenance & Citations**: Official cards showing the exact source document, publication year, category, page number, and original link.

---

## 🛠️ How to Start the Application from Scratch (Step-by-Step)

If you ever restart your computer or want to run this application on another computer, follow these simple steps:

### Method 1: Using Command Prompt / Terminal

#### 1. Open Command Prompt
- Press `Win + R` on your keyboard, type `cmd`, and press Enter.

#### 2. Go to Project Folder
Type this command and press Enter:
```cmd
cd "d:\Stateful Multi-Agent Research Orchestrator"
```

#### 3. Turn On Virtual Environment
Type this command and press Enter:
```cmd
.\venv\Scripts\activate
```

#### 4. Start the Backend Engine (Terminal Window 1)
Type this command and press Enter:
```cmd
uvicorn 5_api.app:app --reload --port 8000
```
*(Leave this window open! It is the engine powering the research graph.)*

#### 5. Start the Web Dashboard (Terminal Window 2)
Open a second Command Prompt window, go to the folder, activate `venv`, and run:
```cmd
python -m http.server 3000 --directory 6_frontend
```

#### 6. Open Browser
Open your web browser and go to:
👉 **`http://localhost:3000`**

---

### Method 2: Using Docker (Single Command!)

If you have **Docker Desktop** installed on your computer:

1. Open Command Prompt.
2. Go to the project folder:
   ```cmd
   cd "d:\Stateful Multi-Agent Research Orchestrator"
   ```
3. Run this single command:
   ```cmd
   docker-compose up --build
   ```
4. Open your browser to **`http://localhost:3000`**.

---

## ❓ Frequently Asked Questions & Troubleshooting

### 1. "The page says 'Error executing research graph'"
- **Cause**: The backend engine (Port 8000) might be stopped.
- **Solution**: Make sure Step 4 above (`uvicorn 5_api.app:app --reload --port 8000`) is active.

### 2. "Why does a query take 15–20 seconds?"
- **Answer**: The system is executing a full 4-agent graph pipeline: Planner ➔ Searcher ➔ Writer ➔ Inspector. It searches through dozens of data chunks in real time to ensure high accuracy.

### 3. "Where can I see the API technical documentation?"
- Open **`http://localhost:8000/docs`** in your web browser.
