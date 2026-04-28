# 🍳 AI Chef – Smart Recipe Suggestor (Python)

## 📌 Overview

AI Chef is an intelligent recipe recommendation system that suggests meals based on the ingredients available with the user.

Unlike traditional apps, it does not require exact ingredients. It uses AI and flexible database queries to generate customized recipes.

---

## 🚀 Download Application

👉 Download the Windows executable (.exe) from the **Releases section** of this repository.

---

## ✨ Features

* 🔍 Ingredient-based smart search
* 🤖 AI-powered recipe customization (Gemini API)
* ☁️ Cloud database using MongoDB Atlas
* 🖥️ Modern GUI built with CustomTkinter
* 📦 Packaged as standalone .exe

---

## 🛠️ Tech Stack

* **Language:** Python
* **GUI:** CustomTkinter
* **Database:** MongoDB Atlas
* **AI:** Google Gemini API
* **Libraries:** pymongo, pandas, customtkinter

---

## ⚙️ How It Works

### Phase 1: Data & Database

* Recipe dataset sourced from Kaggle
* Stored in MongoDB Atlas cloud database
* Initially tested with 50 rows, later scaled

### Phase 2: Backend Upload Script

* CSV processed using pandas
* Data uploaded using pymongo
* Duplicate prevention using `delete_many({})`

### Phase 3: Smart Search Logic

* User input split into list using `.split(',')`
* MongoDB `$regex` + `$and` used for flexible matching
* Finds recipes containing all input ingredients

### Phase 4: GUI (CustomTkinter)

* Dark mode UI
* Scrollable recipe list
* Clickable buttons with popup details
* Used `ast.literal_eval()` to clean ingredient data

### Phase 5: EXE Build

* Built using PyInstaller
* Single file executable
* GUI-based (no terminal window)

---

## 📂 Project Structure

```
ai-chef-python/
│── main.py
│── setup_database.py
│── dataset.csv
│── requirements.txt
│── README.md
```

---

## ⚙️ Installation (For Developers)

### 1. Clone repo

```
git clone https://github.com/your-username/ai-chef-python.git
cd ai-chef-python
```

### 2. Install dependencies

```
pip install -r requirements.txt
```

### 3. Setup environment variables

* MongoDB Atlas connection string
* Google Gemini API key

### 4. Run app

```
python main.py
```

---

## 🎯 Advantages

* Works with limited ingredients
* Saves time in meal planning
* Intelligent and flexible system

---

## 🔮 Future Scope

* 🎤 Voice input
* 🥗 Nutrition tracking
* 🛒 Grocery integration

---

## 👨‍💻 Team Members

* Bhumi Sisodiya
* Yatharth Pandya
* Aaditya Jain
* Manya Gambhir

---

## 📃 License

This project is for educational purposes.
