import customtkinter as ctk
from tkinter import messagebox
from pymongo import MongoClient
import ast
import threading
import google.generativeai as genai
import certifi

# --- 1. STYLING & CONFIGURATION ---
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")
ACCENT_COLOR = "#3b8ed0"
HOVER_COLOR = "#2563eb"
CARD_COLOR = "#1e293b"

CONNECTION_STRING = "mongodb+srv://pandyayatharth007_db_user:admin123@cluster0.rwkirlk.mongodb.net/?retryWrites=true&w=majority"
GEMINI_API_KEY = "AIzaSyBObp34CFTthmLsEhlqNKuVcTOzW0M04R0"

try:
    genai.configure(api_key=GEMINI_API_KEY)
    ai_model = genai.GenerativeModel('gemini-2.5-flash')
except Exception:
    pass 
current_recipes = []
COMMON_INGREDIENTS = [
    "chicken", "beef", "pork", "salmon", "shrimp", "garlic", "onion", 
    "tomato", "potato", "carrot", "broccoli", "cheese", "egg", "milk", 
    "butter", "flour", "sugar", "pasta", "rice", "lemon", "honey", 
    "soy sauce", "olive oil", "spinach", "mushroom"
]
# --- 2. STREAMING HELPER FUNCTION ---
def update_ai_text(textbox, new_text):
    """Safely inserts new text chunk and auto-scrolls down (The Typing Effect)"""
    textbox.configure(state="normal")
    textbox.insert("end", new_text)
    textbox.see("end") 
    textbox.configure(state="disabled")

# --- 3. LOGIC FUNCTIONS ---
def format_recipe_text(raw_string, is_instruction=False):
    try:
        parsed_list = ast.literal_eval(raw_string)
        if isinstance(parsed_list, list):
            if is_instruction:
                return "\n\n".join([f"✨ STEP {i+1}\n{item}" for i, item in enumerate(parsed_list)])
            else:
                return "\n".join([f"📍 {item}" for item in parsed_list])
    except: pass
    return raw_string
def get_suggestions(event):
    text = ingredient_entry.get().lower()
    for widget in suggestion_frame.winfo_children(): widget.destroy()
    if not text: return
    current_word = text.split(',')[-1].strip()
    if len(current_word) < 2: return
    matches = [i for i in COMMON_INGREDIENTS if i.startswith(current_word)][:4]
    for match in matches:
        def select_suggestion(m=match):
            parts = [p.strip() for p in ingredient_entry.get().split(',')]
            parts[-1] = m
            ingredient_entry.delete(0, 'end')
            ingredient_entry.insert(0, ", ".join(parts) + ", ")
            for w in suggestion_frame.winfo_children(): widget.destroy()
            ingredient_entry.focus()
        ctk.CTkButton(suggestion_frame, text=f"🔍 {match}", width=100, height=30, 
                      corner_radius=20, fg_color=CARD_COLOR, border_width=1,
                      border_color=ACCENT_COLOR, hover_color=HOVER_COLOR,
                      command=select_suggestion).pack(side="left", padx=5)
def search_recipes():
    user_input = ingredient_entry.get().strip()
    if not user_input:
        messagebox.showwarning("Empty Search", "Please enter at least one ingredient! 🥬")
        return
    search_button.configure(text="Searching... ⏳", state="disabled")
    app.after(100, lambda: perform_db_query(user_input))
def perform_db_query(user_input):
    global current_recipes
    for widget in results_frame.winfo_children(): widget.destroy()
    current_recipes.clear()
    ingredients = [item.strip() for item in user_input.split(',') if item.strip()]
    try:
        client = MongoClient(CONNECTION_STRING, tlsAllowInvalidCertificates=True)
        collection = client['RecipeDB']['recipes']
        query = {"$and": [{"ingredients": {"$regex": item, "$options": "i"}} for item in ingredients]}
        matching_recipes = list(collection.find(query).limit(20))
        search_button.configure(text="Find Recipes 🍳", state="normal")
        if not matching_recipes:
            ctk.CTkLabel(results_frame, text="No matches found. Try adding salt? 🧂", font=("Roboto", 14)).pack(pady=40)
            return
        for index, recipe in enumerate(matching_recipes):
            current_recipes.append(recipe) 
            title = recipe.get('recipe_title', 'Unknown Recipe').title()
            ctk.CTkButton(results_frame, text=f"🍽️  {title}", anchor="w", height=55,
                          font=("Roboto", 15, "bold"), fg_color="transparent",
                          border_width=1, border_color="#334155", hover_color=CARD_COLOR,
                          command=lambda i=index: show_recipe_details(i)).pack(fill="x", pady=4, padx=10)
    except Exception as e:
        search_button.configure(text="Find Recipes 🍳", state="normal")
        messagebox.showerror("Cloud Error", f"Connection failed! ❌\n{e}")
def show_recipe_details(index):
    selected_recipe = current_recipes[index]
    title = selected_recipe.get('recipe_title', 'Recipe').title()
    detail_window = ctk.CTkToplevel(app)
    detail_window.title(f"Viewing: {title}")
    detail_window.geometry("650x850")
    detail_window.configure(fg_color="#0f172a")
    detail_window.attributes('-topmost', True) 
    
    # Header Section
    header_frame = ctk.CTkFrame(detail_window, fg_color=ACCENT_COLOR, height=100, corner_radius=0)
    header_frame.pack(fill="x")
    ctk.CTkLabel(header_frame, text=f"📖 {title}", font=("Roboto", 24, "bold"), text_color="white", wraplength=550).pack(pady=30)
    
    # Detailed Textbox
    textbox = ctk.CTkTextbox(detail_window, font=("Roboto", 16), wrap="word", corner_radius=15, border_width=2, border_color="#1e293b")
    textbox.pack(fill="both", expand=True, padx=30, pady=(30, 15))
    ing_fmt = format_recipe_text(selected_recipe.get('ingredients', ''), False)
    dir_fmt = format_recipe_text(selected_recipe.get('directions', ''), True)
    content = f"🛒 INGREDIENTS NEEDED\n{'━'*30}\n{ing_fmt}\n\n👨‍🍳 COOKING INSTRUCTIONS\n{'━'*30}\n{dir_fmt}"
    textbox.insert("0.0", content)
    textbox.configure(state="disabled")
    
    # --- GEMINI AI INTEGRATION SECTION ---
    ai_frame = ctk.CTkFrame(detail_window, fg_color=CARD_COLOR, corner_radius=15)
    ai_frame.pack(fill="x", padx=30, pady=(0, 30))
    ai_entry = ctk.CTkEntry(ai_frame, font=("Roboto", 14), placeholder_text="e.g. Make it vegan, scale for 5 people...", height=45)
    ai_entry.pack(side="left", fill="x", expand=True, padx=(15, 10), pady=15)
    ai_entry.bind("<Return>", lambda event: handle_ai_request())
    def handle_ai_request():
        request_text = ai_entry.get().strip()
        if not request_text: return
        if GEMINI_API_KEY == "YOUR_GEMINI_API_KEY_HERE":
            messagebox.showerror("API Key Missing", "Please insert your API Key in main.py")
            return
        ai_btn.configure(text="Thinking... 🧠", state="disabled")
        
        # 1. Open the popup window IMMEDIATELY so the user doesn't wait
        ai_window = ctk.CTkToplevel(app)
        ai_window.title("✨ AI Chef Modifications")
        ai_window.geometry("600x700")
        ai_window.configure(fg_color="#0f172a")
        ai_window.attributes('-topmost', True)
        ctk.CTkLabel(ai_window, text="✨ Your Custom AI Recipe", font=("Roboto", 24, "bold"), text_color=ACCENT_COLOR).pack(pady=20)
        ai_textbox = ctk.CTkTextbox(ai_window, font=("Roboto", 16), wrap="word", corner_radius=15, border_width=2, border_color="#1e293b")
        ai_textbox.pack(fill="both", expand=True, padx=30, pady=(0, 30))
        ai_textbox.configure(state="disabled") # Lock it initially
        def ask_gemini():
            try:
                prompt = f"""
                You are a Master Chef. I have the following recipe:
                Title: {title}
                Ingredients: {ing_fmt}
                Directions: {dir_fmt}
                
                The user has requested this modification: "{request_text}"
                Please rewrite the recipe beautifully to accommodate their request.
                """
                
                # 2. Add 'stream=True' to get words as they are generated
                response = ai_model.generate_content(prompt, stream=True)
                
                # 3. Loop through the words and send them to the UI instantly
                for chunk in response:
                    if chunk.text:
                        # Capture the text chunk safely and update the UI
                        app.after(0, lambda t=chunk.text: update_ai_text(ai_textbox, t))
            except Exception as e:
                app.after(0, lambda: messagebox.showerror("AI Error", f"Something went wrong: {e}"))
            finally:
                app.after(0, lambda: ai_btn.configure(text="Ask AI ✨", state="normal"))
        # Run the API call in the background
        threading.Thread(target=ask_gemini, daemon=True).start()
    ai_btn = ctk.CTkButton(ai_frame, text="Ask AI ✨", font=("Roboto", 14, "bold"), fg_color=ACCENT_COLOR, hover_color=HOVER_COLOR, width=120, height=45, command=handle_ai_request)
    ai_btn.pack(side="right", padx=(0, 15), pady=15)

# --- 4. MAIN GUI SETUP ---
app = ctk.CTk()
app.title("ChefCloud v4.0 - AI Recipe Finder")
app.geometry("850x800")
title_label = ctk.CTkLabel(app, text="ChefCloud ✨", font=("Roboto", 42, "bold"), text_color=ACCENT_COLOR)
title_label.pack(pady=(50, 5))
subtitle = ctk.CTkLabel(app, text="AI Chef • Cloud Database ", font=("Roboto", 15), text_color="#64748b")
subtitle.pack(pady=(0, 30))
search_container = ctk.CTkFrame(app, fg_color="transparent")
search_container.pack(pady=10)
ingredient_entry = ctk.CTkEntry(search_container, font=("Roboto", 17), width=500, height=60, placeholder_text="Enter ingredients (e.g. chicken, salt)...", border_color="#334155", corner_radius=10)
ingredient_entry.pack(side="left", padx=10)
ingredient_entry.bind("<KeyRelease>", get_suggestions)
ingredient_entry.bind("<Return>", lambda event: search_recipes())
search_button = ctk.CTkButton(search_container, text="Find Recipes 🍳", font=("Roboto", 16, "bold"), width=160, height=60, corner_radius=10, fg_color=ACCENT_COLOR, hover_color=HOVER_COLOR, command=search_recipes)
search_button.pack(side="left")
suggestion_frame = ctk.CTkFrame(app, fg_color="transparent")
suggestion_frame.pack(pady=(5, 15))
result_header_frame = ctk.CTkFrame(app, fg_color="transparent")
result_header_frame.pack(fill="x", padx=80)
ctk.CTkLabel(result_header_frame, text="PROPOSED MEALS", font=("Roboto", 13, "bold"), text_color="#64748b").pack(side="left")
ctk.CTkFrame(result_header_frame, height=2, fg_color="#1e293b").pack(side="left", fill="x", expand=True, padx=10)
results_frame = ctk.CTkScrollableFrame(app, width=700, height=450, corner_radius=20, fg_color="#0f172a", border_width=2, border_color="#1e293b")
results_frame.pack(fill="both", expand=True, padx=80, pady=(10, 40))
app.mainloop()