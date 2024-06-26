import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd

print("Wczytywanie danych...")


basics = pd.read_csv('title.basics.tsv', sep='\t', na_values='\\N')
print("Wczytano title.basics.tsv")

ratings = pd.read_csv('title.ratings.tsv', sep='\t', na_values='\\N')
print("Wczytano title.ratings.tsv")


data = pd.merge(basics, ratings, on='tconst')
print("Połączono dane")


data = data[data['titleType'] == 'movie']
print("Przefiltrowano tylko filmy")


data = data.dropna(subset=['primaryTitle', 'genres', 'averageRating', 'startYear'])
print("Dane wyczyszczone")

# Mapowanie gatunków z angielskiego na polski
genre_mapping = {
    'Action': 'Akcja',
    'Comedy': 'Komedia',
    'Drama': 'Dramat',
    'Horror': 'Horror',
    'Romance': 'Romans',
    'Sci-Fi': 'Sci-Fi',
    'Adventure': 'Przygodowy',
    'Animation': 'Animacja',
    'Biography': 'Biograficzny',
    'Crime': 'Kryminalny',
    'Documentary': 'Dokumentalny',
    'Family': 'Familijny',
    'Fantasy': 'Fantasy',
    'History': 'Historyczny',
    'Music': 'Muzyczny',
    'Mystery': 'Tajemnica',
    'Thriller': 'Thriller',
    'War': 'Wojenny',
    'Western': 'Western'
}


inverse_genre_mapping = {v: k for k, v in genre_mapping.items()}


all_genres = sorted(genre_mapping.values())

# Wyciąganie unikalnych lat produkcji filmów
data['startYear'] = data['startYear'].astype(int)  # Konwersja na int, aby usunąć końcówki dziesiętne
all_years = sorted(data['startYear'].unique(), reverse=True)

# Inicjalizacja okna głównego

root = tk.Tk()
root.title("Rekomendacje Filmów i Seriali")

# Pobierz rozdzielczość ekranu
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# Oblicz wymiary okna (50% rozdzielczości ekranu)
window_width = int(screen_width * 0.5)
window_height = int(screen_height * 0.5)


root.geometry(f"{window_width}x{window_height}")

# Opcjonalnie: wyśrodkuj okno na ekranie
root.update_idletasks()
x = (screen_width - window_width) // 2
y = (screen_height - window_height) // 2
root.geometry(f"+{x}+{y}")

root.configure(bg="#2C3E50")

# Style
style = ttk.Style()
style.configure("TFrame", background="#2C3E50")
style.configure("TLabel", background="#2C3E50", foreground="#ECF0F1", font=("Helvetica", 12))
style.configure("TButton", background="#3498DB", foreground="#ECF0F1", font=("Helvetica", 12))
style.configure("TCombobox", font=("Helvetica", 12))
style.configure("TEntry", font=("Helvetica", 12))
style.map("TButton", background=[("active", "#2980B9")])
style.configure("Red.TButton", foreground="red")


# Funkcja rekomendacji
def recommend():
    genre_pl = genre_var.get()
    genre_en = inverse_genre_mapping.get(genre_pl)
    if not genre_en:
        messagebox.showerror("Błąd", "Proszę wybrać prawidłowy gatunek.")
        return

    try:
        min_rating = float(rating_var.get())
    except ValueError:
        messagebox.showerror("Błąd", "Proszę wprowadzić prawidłową ocenę.")
        return

    try:
        selected_year = int(year_var.get())
    except ValueError:
        messagebox.showerror("Błąd", "Proszę wybrać prawidłowy rok produkcji.")
        return

    try:
        min_votes = int(min_votes_var.get())
    except ValueError:
        messagebox.showerror("Błąd", "Proszę wprowadzić prawidłową minimalną liczbę głosów.")
        return

    recommendations = data[
        (data['genres'].str.contains(genre_en, case=False)) &
        (data['averageRating'] >= min_rating) &
        (data['startYear'] == selected_year) &
        (data['numVotes'] >= min_votes)
    ]
    recommendations = recommendations.sort_values(by='averageRating')

    if recommendations.empty:
        messagebox.showinfo("Brak rekomendacji", "Nie znaleziono filmów spełniających kryteria.")
    else:
        result_text.delete(1.0, tk.END)  # Czyszczenie wcześniejszych wyników
        for index, row in recommendations.iterrows():
            result_text.insert(tk.END, f"{row['primaryTitle']} ({int(row['startYear'])}) - {row['averageRating']} - ({row['numVotes']} głosów)\n")
        result_count_label.config(text=f"Liczba wyników: {len(recommendations)}")

def random_recommend():
    try:
        num_recommendations = int(random_count_var.get())
        if num_recommendations <= 0:
            raise ValueError
    except ValueError:
        messagebox.showerror("Błąd", "Proszę wprowadzić prawidłową liczbę rekomendacji.")
        return

    random_samples = data.sample(n=num_recommendations)

    result_text.delete(1.0, tk.END)
    for index, row in random_samples.iterrows():
        result_text.insert(tk.END, f"{row['primaryTitle']} ({int(row['startYear'])}) - {row['averageRating']} ({row['numVotes']} głosów)\n")
    result_count_label.config(text=f"Liczba wyników: {len(random_samples)}")
# Funkcja do czyszczenia wyników
def clear_results():
    result_text.delete(1.0, tk.END)
    result_count_label.config(text="")


# Tworzenie głównej ramki
mainframe = ttk.Frame(root, padding="20")
mainframe.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

# Etykiety i pola wyboru
ttk.Label(mainframe, text="Wybierz gatunek:").grid(column=0, row=0, padx=10, pady=10, sticky=tk.W)
genre_var = tk.StringVar()
genre_combobox = ttk.Combobox(mainframe, textvariable=genre_var, values=all_genres, state='readonly')
genre_combobox.grid(column=1, row=0, padx=10, pady=10, sticky=(tk.W, tk.E))

ttk.Label(mainframe, text="Minimalna ocena (0-10):").grid(column=0, row=1, padx=10, pady=10, sticky=tk.W)
rating_var = tk.StringVar()
rating_entry = ttk.Entry(mainframe, textvariable=rating_var)
rating_entry.grid(column=1, row=1, padx=10, pady=10, sticky=(tk.W, tk.E))

ttk.Label(mainframe, text="Minimalna liczba głosów:").grid(column=0, row=3, padx=10, pady=10, sticky=tk.W)
min_votes_var = tk.StringVar()
min_votes_entry = ttk.Entry(mainframe, textvariable=min_votes_var)
min_votes_entry.grid(column=1, row=3, padx=10, pady=10, sticky=(tk.W, tk.E))

ttk.Label(mainframe, text="Wybierz rok produkcji:").grid(column=0, row=2, padx=10, pady=10, sticky=tk.W)
year_var = tk.StringVar()
year_combobox = ttk.Combobox(mainframe, textvariable=year_var, values=all_years, state='readonly')
year_combobox.grid(column=1, row=2, padx=10, pady=10, sticky=(tk.W, tk.E))

# Przycisk rekomendacji
recommend_button = ttk.Button(mainframe, text="Rekomenduj", command=recommend)
recommend_button.grid(column=0, row=4, columnspan=2, pady=10)

random_button = ttk.Button(mainframe, text="Losuj rekomendacje", command=random_recommend)
random_button.grid(column=0, row=8, columnspan=2, pady=10)

ttk.Label(mainframe, text="Liczba rekomendacji:").grid(column=0, row=8, padx=10, pady=10, sticky=tk.W)
random_count_var = tk.StringVar()
random_count_entry = ttk.Entry(mainframe, textvariable=random_count_var)
random_count_entry.grid(column=1, row=9, padx=10, pady=10, sticky=(tk.W, tk.E))

# Przycisk czyszczenia wyników
clear_button = ttk.Button(mainframe, text="Wyczyść", command=clear_results)
clear_button.grid(column=0, row=5, columnspan=2, pady=10)


result_frame = ttk.Frame(mainframe, borderwidth=2, relief="sunken")
result_frame.grid(column=0, row=6, columnspan=2, pady=10, sticky=(tk.W, tk.E, tk.N, tk.S))

result_text = tk.Text(result_frame, height=10, wrap="word", state="normal", bg="#ECF0F1", fg="#2C3E50",
                      font=("Helvetica", 12))
result_text.pack(side="left", fill="both", expand=True)

scrollbar = ttk.Scrollbar(result_frame, orient="vertical", command=result_text.yview)
scrollbar.pack(side="right", fill="y")

result_text.config(yscrollcommand=scrollbar.set)


result_count_label = ttk.Label(mainframe, text="", font=("Helvetica", 12))
result_count_label.grid(column=0, row=7, columnspan=2, pady=5)


print("Uruchamianie aplikacji...")
root.mainloop()
print("Aplikacja uruchomiona")
