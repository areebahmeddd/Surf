import time
import subprocess
import webbrowser

import tkinter as tk
from tkinter import ttk, messagebox

from engine import text_search, image_search

def initialize_gui():
    global search_query_entry

    # Create the primary window for Surf application
    primary_window = tk.Tk()
    primary_window.title("Surf [v1.0]")
    primary_window.geometry("600x200")

    # Create a frame to hold the search query components
    search_query_frame = ttk.Frame(primary_window, padding = (0, 20))
    search_query_frame.pack()

    # Create a label for the search query
    search_query_label = ttk.Label(search_query_frame, text = "Search Query", font = ("Helvetica", 14, "bold"))
    search_query_label.pack(side = tk.LEFT)

    # Create an entry field for the search query
    search_query_entry = ttk.Entry(search_query_frame, font = ("Helvetica", 14))
    search_query_entry.pack(side = tk.LEFT, padx = (10, 0))
    search_query_entry.bind("<Return>", lambda event: display_results())

    # Create a frame to hold the upload image components
    upload_image_frame = ttk.Frame(primary_window, padding = (0, 10))
    upload_image_frame.pack()

    # Create a label for the upload image
    upload_image_label = ttk.Label(upload_image_frame, text = "Upload Image", font = ("Helvetica", 14, "bold"))
    upload_image_label.pack(side = tk.LEFT)

    # Create an entry field for the upload image
    upload_image_entry = ttk.Entry(upload_image_frame, font = ("Helvetica", 14))
    upload_image_entry.pack(side = tk.LEFT, padx = (10, 0))
    upload_image_entry.bind("<Button-1>", lambda event: image_search())

    # Define the style for the buttons
    style = ttk.Style()
    style.configure("Custom.TButton", font = ("Helvetica", 14), padding = (10, 8))

    # Create a frame to hold the buttons
    button_frame = ttk.Frame(primary_window, padding = (0, 20))
    button_frame.pack()

    # Create the Clear button
    clear_button = ttk.Button(button_frame, text = "Clear", command = clear_results, style = "Custom.TButton")
    clear_button.pack(side = tk.LEFT, padx = (0, 10))

    # Create the Search button
    search_button = ttk.Button(button_frame, text = "Search", command = display_results, style = "Custom.TButton")
    search_button.pack(side = tk.LEFT)

    # Create the Refresh button
    refresh_button = ttk.Button(button_frame, text = "Refresh", command = refresh_results, style = "Custom.TButton")
    refresh_button.pack(side = tk.RIGHT, padx = (10, 0))

    primary_window.mainloop()

def display_results():
    global secondary_window

    # Retrieve the user search query
    search_query = search_query_entry.get().strip()

    if not search_query:
        messagebox.showwarning("Surf", "Invalid search query")
        return
    else:
        # Measure the search execution time and the number of results
        start_time = time.time()
        search_results = text_search(search_query)
        end_time = time.time()

        search_time = end_time - start_time
        result_count = len(search_results)

    if not search_results:
        messagebox.showinfo("Surf", "No results found")
        return
    else:
        # Create the secondary window for Surf application
        secondary_window = tk.Toplevel()
        secondary_window.title("Surf [v1.0]")
        secondary_window.geometry("870x650")

        # Create a scrollbar for the search results
        scrollbar = ttk.Scrollbar(secondary_window)
        scrollbar.pack(side = tk.RIGHT, fill = tk.Y)

        # Create a canvas to hold the search results and configure the scrollbar to control the canvas view
        canvas = tk.Canvas(secondary_window, yscrollcommand = scrollbar.set)
        canvas.pack(side = tk.LEFT, fill = tk.BOTH, expand = True)
        scrollbar.config(command = canvas.yview)

        # Create a frame within the canvas to hold the search result components
        frame = ttk.Frame(canvas)
        frame.pack(padx = 10, pady = 10)

        # Create a label to display the search results count and execution time
        label = ttk.Label(frame, text = f"Search Results ({result_count}, {search_time:.2f})", font = ("Helvetica", 20, "bold"))
        label.pack(padx = 5)

        # Create a scrollable window and adjust the scroll region on resize
        canvas.create_window((0, 0), window = frame, anchor = "nw")
        canvas.bind("<Configure>", lambda event: canvas.configure(scrollregion = canvas.bbox("all")))

        for result in search_results:
            # Create a frame to display the result
            result_frame = ttk.Frame(frame, padding = 10, relief = "ridge")
            result_frame.pack(fill = tk.BOTH, padx = 10, pady = 5)

            # Create a label to display the title of the result
            title_label = ttk.Label(result_frame, text = result["title"], font = ("Helvetica", 18, "bold"), wraplength = 800)
            title_label.pack(anchor = "w")

            # Create a label to display the link of the result
            link_label = ttk.Label(result_frame, text = result["link"], font = ("Helvetica", 18), wraplength = 800, foreground = "blue", cursor = "hand2")
            link_label.pack(anchor = "w")

            # Check the search engine of the result and bind the link label with appropriate action
            if result["engine"] == "google":
                chrome_path = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
                link_label.bind("<Button-1>", lambda event, link = result["link"]: subprocess.Popen([chrome_path, link]))
            elif result["engine"] == "bing":
                edge_path = "C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe"
                link_label.bind("<Button-1>", lambda event, link = result["link"]: subprocess.Popen([edge_path, link]))
            else:
                link_label.bind("<Button-1>", lambda event, link = result["link"]: webbrowser.open_new(link))

            # Add a horizontal separator
            ttk.Separator(result_frame, orient = tk.HORIZONTAL).pack(fill = tk.X, padx = 5, pady = 5)

            # Create a label to display the search engine of the result
            engine_label = ttk.Label(result_frame, text = f'Search Engine: {result["engine"]}', font = ("Helvetica", 16, "bold"))
            engine_label.pack()

        # Bind the mouse wheel event to scroll the canvas
        canvas.bind_all("<MouseWheel>", lambda event: canvas.yview_scroll(int(-1 * (event.delta / 120)), "units"))

        secondary_window.mainloop()

def clear_results():
    search_query_entry.delete(0, tk.END)
    secondary_window.destroy()

def refresh_results():
    secondary_window.destroy()
    display_results()

initialize_gui()