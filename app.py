#!/usr/bin/env python3


import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import ImageTk, Image
import sqlite3
import os
from qwikidata.linked_data_interface import get_entity_dict_from_api
from SPARQLWrapper import SPARQLWrapper, JSON
import hashlib
import urllib.request
import io
from random import choice

import database_functions
from artworks import Artworks
from artists import Artists


class MomaGuiApp:
    """Η κλάση της γραφικής διεπαφής της εφαρμογής"""

    def __init__(self, root):
        self.root = root
        self.root.title("Museum Of Modern Art (Moma) Project")
        self.root.geometry("1600x1024")
        self.font = "saucecodepronerdfont"
        self.pads = {
            "padx": 3,
            "pady": 3,
        }
        self.button_options = {
            "highlightthickness": 0,
            "font": f"{self.font} 10 bold",
            "bg": "#353535",
            "fg": "#858585",
            "activebackground": "#252525",
            "activeforeground": "#87af5f",
            "relief": "flat",
        }

        self.label_options = {
            "bd": 0,
            "highlightthickness": 0,
            "fg": "#87af5f",
            "bg": "#404040",
            "font": f"{self.font} 8",
        }

        self.entry_options = {
            "bd": 0,
            "highlightthickness": 0,
            "bg": "#555555",
            "fg": "#202020",
            "font": f"{self.font} 10",
            "justify": "left",
        }
        self.translations = {
            "title": "Τίτλος",
            "department": "Τμήμα",
            "artist": "Καλλιτέχνης",
            "nationality": "Εθνικότητα",
            "gender": "Φύλο",
            "begindate": "Έτος γέννησης",
            "enddate": "Έτος θανάτου",
            "dimensions": "Διαστάσεις ή διάρκεια",
            "date": "Χρονολογία",
            "dateacquired": "Ημερομηνία απόκτησης",
            "medium": "Μέσο",
            "creditline": "Προέλευση",
        }
        ## Φόρτωση της βάσης δεδομένων σε dataframe
        self.full_df = database_functions.search_database()
        # self.artworks_table_columns = database_functions.get_table_columns("artworks")
        self.selected_object_id = None
        self.last_focused = None
        self.widgets()

    def widgets(self):
        def draw_side_bar():
            """Συνάρτηση σχεδίασης του sidebar"""

            self.sidebar_frame.pack(expand=0, side="left", fill="both", **self.pads)
            self.sidebar_upper_frame.pack(expand=0, fill="both", **self.pads)
            self.logolabel.pack(expand=0, fill="both", **self.pads)
            self.buttons_frame.pack(expand=0, fill="both", **self.pads)
            self.b2.pack(expand=1, fill="x", side="left", **self.pads)
            self.b4.pack(expand=1, fill="x", side="right", **self.pads)
            self.exit_button_frame.pack(expand=0, side="bottom", fill="x", **self.pads)
            self.random_artwork_button.pack(expand=1, fill="x", **self.pads)
            self.exit_button.pack(expand=0, side="bottom", fill="x", **self.pads)

        ##  Γραφικά στοιχεία
        self.base_frame = tk.Frame(self.root, bg="#202020")
        self.main_frame = tk.Frame(self.base_frame, bg="#252525")

        self.moma_label_frame = tk.Frame(
            self.base_frame,
            bg="#303030",
        )

        self.center_frame = tk.Frame(
            self.main_frame,
            bg="#353535",
        )

        self.right_frame = tk.Frame(
            self.main_frame,
            bg="#353535",
            width=50,
        )

        self.sidebar_frame = tk.Frame(
            self.main_frame,
            bg="#353535",
            width=50,
        )

        self.sidebar_upper_frame = tk.Frame(
            self.sidebar_frame,
            bg="#404040",
            width=50,
        )

        ## Δημιουργία και σχεδίαση του logo
        self.logo_path = "files/images/moma_logo.jpg"
        self.logo = ImageTk.PhotoImage(Image.open(self.logo_path))
        self.logolabel = tk.Label(
            self.sidebar_upper_frame, bg="#9aa4a6", image=self.logo
        )
        self.logolabel.image = self.logo

        ## Δημιουργία ενος frame με κουμπιά στο sidebar
        self.buttons_frame = tk.Frame(
            self.sidebar_frame,
            height=200,
            bg="#404040",
            width=50,
        )

        self.b2 = tk.Button(
            self.buttons_frame,
            text=" Προσθήκη ",
            command=self.add_form,
            **self.button_options,
        )

        self.b4 = tk.Button(
            self.buttons_frame,
            text=" Σύνθετη αναζήτηση ",
            command=self.search_form,
            **self.button_options,
        )

        ## Δημιουργία frame που θα φέρει φόρμα για χρήση σε αναζήτηση και προσθήκη
        self.sidebar_lower_frame = tk.Frame(
            self.sidebar_frame,
            bg="#404040",
            width=50,
        )

        self.form1 = tk.LabelFrame(
            self.sidebar_lower_frame,
            text="ΤΙΤΛΟΣ",
            **self.label_options,
        )

        self.e1 = tk.Entry(
            self.form1,
            **self.entry_options,
        )

        self.form2 = tk.LabelFrame(
            self.sidebar_lower_frame,
            text="ΚΑΛΛΙΤΕΧΝΗΣ",
            **self.label_options,
        )

        self.e2 = tk.Entry(
            self.form2,
            **self.entry_options,
        )

        self.form3 = tk.LabelFrame(
            self.sidebar_lower_frame,
            text="ΕΘΝΙΚΟΤΗΤΑ",
            **self.label_options,
        )

        self.e3 = tk.Entry(
            self.form3,
            **self.entry_options,
        )

        self.form4 = tk.LabelFrame(
            self.sidebar_lower_frame,
            text="ΦΥΛΟ",
            **self.label_options,
        )

        self.e4 = tk.Entry(
            self.form4,
            **self.entry_options,
        )

        self.form5 = tk.LabelFrame(
            self.sidebar_lower_frame,
            text="ΔΙΑΣΤΑΣΕΙΣ Ή ΔΙΑΡΚΕΙΑ",
            **self.label_options,
        )

        self.e5 = tk.Entry(
            self.form5,
            **self.entry_options,
        )

        self.form7 = tk.LabelFrame(
            self.sidebar_lower_frame,
            text="ΧΡΟΝΟΛΟΓΙΑ ΕΡΓΟΥ",
            **self.label_options,
        )

        self.e7 = tk.Entry(
            self.form7,
            **self.entry_options,
        )

        self.form8 = tk.LabelFrame(
            self.sidebar_lower_frame,
            text="ΗΜΕΡΟΜΗΝΙΑ ΑΠΟΚΤΗΣΗΣ",
            **self.label_options,
        )

        self.e8 = tk.Entry(
            self.form8,
            **self.entry_options,
        )

        self.form9 = tk.LabelFrame(
            self.sidebar_lower_frame,
            text="ΜΕΣΟ ΕΡΓΟΥ",
            **self.label_options,
        )

        self.e9 = tk.Entry(
            self.form9,
            **self.entry_options,
        )

        self.form10 = tk.LabelFrame(
            self.sidebar_lower_frame,
            text="ΕΤΟΣ ΓΕΝΝΗΣΗΣ",
            **self.label_options,
        )

        self.e10 = tk.Entry(
            self.form10,
            **self.entry_options,
        )

        self.form11 = tk.LabelFrame(
            self.sidebar_lower_frame,
            text="ΕΤΟΣ ΘΑΝΑΤΟΥ",
            **self.label_options,
        )

        self.e11 = tk.Entry(
            self.form11,
            **self.entry_options,
        )

        self.form12 = tk.LabelFrame(
            self.sidebar_lower_frame,
            text="URL ΕΡΓΟΥ",
            **self.label_options,
        )

        self.e12 = tk.Entry(
            self.form12,
            **self.entry_options,
        )

        self.form13 = tk.LabelFrame(
            self.sidebar_lower_frame,
            text="URL ΕΙΚΟΝΑΣ",
            **self.label_options,
        )

        self.e13 = tk.Entry(
            self.form13,
            **self.entry_options,
        )

        self.form14 = tk.LabelFrame(
            self.sidebar_lower_frame,
            text="ΤΜΗΜΑ",
            **self.label_options,
        )

        self.e14 = tk.Entry(
            self.form14,
            **self.entry_options,
        )

        self.selected_label = tk.Label(
            self.sidebar_lower_frame,
            width=40,
            **self.label_options,
        )

        self.open_artwork_tab = tk.Button(
            self.sidebar_lower_frame, text=" Καρτέλα έργου ", **self.button_options
        )

        self.open_artist_tab = tk.Button(
            self.sidebar_lower_frame, text=" Καρτέλα καλλιτέχνη ", **self.button_options
        )

        self.update_button = tk.Button(
            self.sidebar_lower_frame,
            text=" Ενημέρωση στοιχείων έργου ",
            **self.button_options,
        )

        self.form_button = tk.Button(
            self.sidebar_lower_frame, text=" Αναζήτηση ", **self.button_options
        )

        ## Δημιουργία κουμπιού εξόδου
        self.exit_button_frame = tk.Frame(
            self.sidebar_frame,
            bg="#404040",
            width=50,
        )

        self.exit_button = tk.Button(
            self.exit_button_frame,
            text="Έξοδος",
            command=self.root.quit,
            **self.button_options,
        )

        self.random_artwork_button = tk.Button(
            self.exit_button_frame,
            text=" Επιλογή έργου στην τύχη ",
            **self.button_options,
            command=self.select_random_artwork,
        )

        ## Ρύθμιση του ttk theme του πίνακα (αντικείμενο treeview)
        # print(self.table.winfo_class())  <--  βρίσκω το όνομα της κλάσης για
        #                                       να ρυθμίσω το theme
        mystyle = ttk.Style()
        mystyle.theme_use("clam")
        mystyle.configure(
            "mystyle.Treeview", background="#404040", foreground="#858585"
        )
        mystyle.configure("mystyle.Treeview", font=f"{self.font} 10")  # Fonts πίνακα
        # Fonts των επικεφαλίδων
        mystyle.configure(
            "mystyle.Treeview.Heading",
            font=f"{self.font} 10 bold",
            background="#303030",
            foreground="#87af5f",
            bd=1,
            relief="flat",
        )
        # Χωρίς borders
        mystyle.layout(
            "mystyle.Treeview", [("mystyle.Treeview.treearea", {"sticky": "nswe"})]
        )
        # Στυλ των scrollbars
        mystyle.configure(
            "TScrollbar",
            gripcount=0,
            lightcolor="#353535",
            darkcolor="#202020",
            background="#87af5f",
            troughcolor="#303030",
            bordercolor="#252525",
            arrowsize=15,
            arrowcolor="#404040",
        )

        self.base_frame.pack(expand=1, fill="both", **self.pads)
        self.main_frame.pack(expand=1, fill="both", **self.pads)
        draw_side_bar()
        self.center_frame.pack(expand=1, side="left", fill="both", **self.pads)

        self.draw_table(self.full_df)
        self.select_first_table_row()

    def select_first_table_row(self):
        """Μέθοδος που επιλέγει το πρώτο έργο του πίνακα όταν κλήθεί
        και το εμφανίζει στο sidebar"""
        self.table.focus_set()
        child_id = self.table.get_children()[0]
        self.table.focus(child_id)
        self.table.selection_set(child_id)
        self.select_table_row()
        self.show_selected()

    def draw_table(self, df):
        """Μέθοδος για την δημιουργία και σχεδίαση του πίνακα"""

        def open_stats_frame():
            """Συνάρτηση για εναλλαγή μεταξύ πίνακα και των στατιστικών charts"""

            for widget in self.stats_frame.winfo_children():
                for figure in widget.winfo_children():
                    figure.destroy()
            draw_charts("ΚΑΛΛΙΤΈΧΝΗΣ", self.stat_box_1)
            draw_charts("ΕΘΝΙΚΌΤΗΤΑ", self.stat_box_2)
            draw_charts("ΦΎΛΟ", self.stat_box_2)
            draw_charts("ΧΡΟΝΟΛΟΓΊΑ ΈΡΓΟΥ", self.stat_box_3)

            if self.stats_frame.winfo_ismapped():
                self.show_results_frame.pack(
                    expand=1, side="bottom", fill="both", **self.pads
                )
                self.open_stats_button.bind("<1>", self.stats_frame.pack_forget())

            else:
                self.show_results_frame.pack_forget()
                self.open_stats_button.bind(
                    "<1>",
                    self.stats_frame.pack(
                        expand=1, side="top", fill="both", **self.pads
                    ),
                )

        ## Συνάρτηση για την κατασκευή των plots με τα στατιστικά
        ## Αναφορά από https://datatofish.com/matplotlib-charts-tkinter-gui/
        def draw_charts(by, where):
            figure = plt.Figure()
            figure.set_tight_layout(True)
            ax = figure.add_subplot(111)
            ax.set_facecolor("#454545")
            ax.xaxis.label.set_color("#87af5f")
            ax.yaxis.label.set_color("#87af5f")
            ax.tick_params(axis="x", colors="#858585")
            ax.tick_params(axis="y", colors="#858585")
            figure.set_facecolor("#404040")
            chart = FigureCanvasTkAgg(figure, where)
            chart.get_tk_widget().pack(expand=1, fill="both", **self.pads)
            df_by = df.groupby(by).size()
            df_by.plot(kind="barh", legend=False, ax=ax, color="orange")
            by = by[:-1] if by.endswith("Σ") else by
            ax.set_title(f"ΚΑΤΑΝΟΜΗ ΑΝΑ {by}", color="#87af5f")

        self.stats_frame = tk.Frame(
            self.center_frame,
            bg="#353535",
        )

        self.stat_box_1 = tk.Frame(
            self.stats_frame,
            bg="#404040",
        )
        self.stat_box_1.pack(expand=1, side="left", fill="both", **self.pads)

        self.stat_box_2 = tk.Frame(
            self.stats_frame,
            bg="#404040",
        )
        self.stat_box_2.pack(expand=1, side="left", fill="both", **self.pads)

        self.stat_box_3 = tk.Frame(
            self.stats_frame,
            bg="#404040",
        )
        self.stat_box_3.pack(expand=1, side="left", fill="both", **self.pads)

        self.stat_box_4 = tk.Frame(
            self.stats_frame,
            bg="#404040",
        )
        self.stat_box_4.pack(expand=1, side="left", fill="both", **self.pads)

        self.stat_box_5 = tk.Frame(
            self.stats_frame,
            bg="#404040",
        )
        self.stat_box_5.pack(expand=1, side="left", fill="both", **self.pads)

        self.show_results_frame = tk.Frame(self.center_frame, bg="#353535")

        ## Δημιουργία και σχεδίαση του πίνακα table (αντικείμενο treeview)
        self.table = ttk.Treeview(self.show_results_frame, style="mystyle.Treeview")

        ## Δημιουργια των scrollbars του πίνακα
        self.hor_scrollbar = ttk.Scrollbar(
            self.show_results_frame,
            orient=tk.HORIZONTAL,
            command=self.table.xview,
        )
        self.table.configure(xscroll=self.hor_scrollbar.set)

        self.ver_scrollbar = ttk.Scrollbar(
            self.show_results_frame, orient=tk.VERTICAL, command=self.table.yview
        )
        self.table.configure(yscroll=self.ver_scrollbar.set)

        ## Δημιουργία κουμπιού για το άνοιγμα των στατιστικών
        self.open_stats_button_frame = tk.Frame(
            self.center_frame,
            bg="#404040",
        )
        self.open_stats_button = tk.Button(
            self.open_stats_button_frame,
            text=" Στατιστικά στοιχεία ",
            command=open_stats_frame,
            **self.button_options,
        )
        ## Εμφάνιση του πλήθους αποτελεσμάτων της αναζήτησης σε label
        self.results_number = tk.Label(
            self.open_stats_button_frame,
            text=f"ΠΛΗΘΟΣ ΕΡΓΩΝ: {df.shape[0]}",
            **self.label_options,
        )
        self.results_number.config(font=f"{self.font} 10 bold")

        self.open_stats_button_frame.pack(expand=0, fill="x", **self.pads)
        self.results_number.pack(expand=0, side="left", fill="x", **self.pads)
        self.open_stats_button.pack(expand=0, side="right", fill="x", **self.pads)

        self.show_results_frame.pack(expand=1, side="bottom", fill="both", **self.pads)
        self.ver_scrollbar.pack(expand=0, fill="y", side="right")
        self.hor_scrollbar.pack(expand=0, fill="x", side="bottom")
        self.table.pack(expand=1, fill="both", **self.pads)
        self.table.bind("<ButtonRelease-1>", self.select_table_row)
        self.bind_arrow_keys(self.table, self.select_table_row)
        self.table.bind("<Return>", self.create_artwork_tab)
        self.table.bind("<Shift-Return>", self.create_artist_tab)

        ## Προετοιμασία του πίνακα
        self.table["columns"] = list(df.columns)
        self.table["show"] = "headings"  ## απόκρυψη πρώτης κενής στήλης
        for col in df.columns:
            self.table.column(col, stretch=True, anchor="center")
            self.table.heading(col, text=f"{col}")

        ## Εισαγωγή δεδομένων στον πίνακα
        for i in range(0, df.shape[0]):
            self.table.insert("", "end", values=list(df.iloc[i]))

        ## Ταξινόμηση στηλών
        def treeview_sort_column(treeview_object, col, reverse):
            """Συνάρτηση για την ταξινόμηση των στηλών του πίνακα με κλικ στα headings"""
            ## Αναφορά από https://stackoverflow.com/questions/1966929/tk-treeview-column-sort

            l = [
                (treeview_object.set(k, col), k)
                for k in treeview_object.get_children("")
            ]
            l.sort(reverse=reverse)

            # Ταξινόμηση ανά στήλη
            for index, (val, k) in enumerate(l):
                treeview_object.move(k, "", index)

            # Αντιστροφή ταξινόμησης με το επόμενο κλικ
            treeview_object.heading(
                col,
                command=lambda: treeview_sort_column(treeview_object, col, not reverse),
            )

        for col in self.table["columns"]:
            self.table.heading(
                col,
                text=col,
                command=lambda _col=col: treeview_sort_column(self.table, _col, False),
            )

    def select_table_row(self, event=None):
        """Μέθοδος για την επιλογή έργου και επιστροφή των περιεχομένων της σχετικής εγγραφής"""

        self.abstract, self.thumb_url = "", ""
        self.selected = self.table.focus()
        self.selected_row_values = self.table.item(self.selected)["values"]
        self.selected_object_id = self.table.item(self.selected)["values"][-1]
        if self.selected_object_id:

            self.row_values = database_functions.get_info_by_objectid(
                self.selected_object_id
            )

            self.aw = Artworks(*self.row_values)
            self.artist_info = database_functions.get_artist_info_by_constituentid(
                self.aw.constituentid
            )
            # print(self.artist_info)
            self.ar = Artists(*self.artist_info)

            # print("\n------artwork--------")
            # for k, v in vars(self.aw).items():
            # print(f"{k} ->  {v}")
            # print("\n------artist--------")
            # for k, v in vars(self.ar).items():
            # print(f"{k} ->  {v}")

            msg = f"\n\nΤίτλος\n{self.aw.title}\n\n\nΚαλλιτέχνης\n{self.aw.artist}"

            ## γραφικά στοιχεία καρτέλας έργου
            self.artwork_tab_frame = tk.LabelFrame(
                self.center_frame,
                text=f"{self.aw.title} by {self.aw.artist}",
                **self.label_options,
            )

            self.artwork_tab_info_frame = tk.Frame(
                self.artwork_tab_frame,
                bg="#404040",
            )

            self.artwork_tab_info_label = tk.Label(
                self.artwork_tab_info_frame,
                **self.label_options,
            )

            self.image_button_frame = tk.Frame(
                self.artwork_tab_info_label,
                bg="#404040",
                width=50,
            )

            self.image_button = tk.Button(
                self.image_button_frame,
                text=" Προβολή έργου ",
                command=None,
                **self.button_options,
            )

            # self.return_button_frame = tk.Frame(
            # self.artwork_tab_info_label,
            # bg="#404040",
            # width=50,
            # )

            self.return_button = tk.Button(
                self.image_button_frame,
                text=" Επιστροφή ",
                command=self.hide_artwork_tab,
                **self.button_options,
            )

            ## γραφικά στοιχεία καρτέλας καλλιτέχνη
            self.artist_tab_frame = tk.LabelFrame(
                self.center_frame,
                text=f"{self.aw.artist}",
                **self.label_options,
            )

            self.artist_tab_info_frame = tk.Frame(
                self.artist_tab_frame,
                bg="#404040",
            )

            self.artist_tab_info_label = tk.Label(
                self.artist_tab_info_frame,
                **self.label_options,
            )

            self.artist_image_button_frame = tk.Frame(
                self.artist_tab_info_label,
                bg="#404040",
                width=50,
            )

            self.artist_image_button = tk.Button(
                self.artist_image_button_frame,
                text=" Προβολή φωτογραφίας ",
                command=None,
                **self.button_options,
            )

            # self.artist_return_button_frame = tk.Frame(
            # self.artist_tab_info_label,
            # bg="#404040",
            # width=50,
            # )

            self.artist_return_button = tk.Button(
                self.artist_image_button_frame,
                text=" Επιστροφή ",
                command=self.hide_artist_tab,
                **self.button_options,
            )

            self.artist_abstract = tk.LabelFrame(
                self.artist_tab_info_label,
                text=f"Σύντομη βιογραφία",
                **self.label_options,
            )

            self.artist_abstract_info_label = tk.Text(
                self.artist_abstract,
                **self.label_options,
            )

            ## Δημιουργία αντικειμένου ListBox για την εμφάνιση των υπόλοιπων έργων από
            ## τον ίδιο καλλιτέχνη που είναι διαθέσιμα
            self.available_artworks = tk.LabelFrame(
                self.artist_tab_info_label,
                text=f"Έργα του ίδιου καλλιτέχνη που είναι διαθέσιμα",
                **self.label_options,
            )

            self.available_artworks_names = tk.Listbox(
                self.available_artworks,
                selectbackground="#393939",
                selectforeground="#f4bf75",
                height=20,
                **self.label_options,
            )

            self.selected_label.config(
                text=msg, fg="#f4bf75", font=f"{self.font} 10 bold", wraplength=400
            )
            self.sidebar_lower_frame.pack(expand=1, fill="both", **self.pads)
            self.show_selected()
            self.b2.config(state="normal")
            self.b4.config(state="normal")
        return self.selected_row_values, self.selected_object_id

    def bind_arrow_keys(self, frame, method):
        """Μέθοδος που κάνει bind τα arrow keys του πληκτρολογίου
        με συγκεκριμένη συνάρτηση και γραφικό στοιχείο"""

        frame.bind("<KeyRelease-Up>", method)
        frame.bind("<KeyRelease-Down>", method)

    def open_form(self, mode):
        """Μέθοδος που ανοίγει τά μενού που χρησιμοποιούνται στην προσθήκη, διαγραφή και αναζήτηση"""

        self.hide_selected()
        self.sidebar_lower_frame.pack(expand=1, fill="both", **self.pads)

        self.b2.pack(expand=1, fill="x", side="left", **self.pads)
        self.b4.pack(expand=1, fill="x", side="right", **self.pads)

        self.form1.pack(expand=0, fill="both", **self.pads)
        self.e1.pack(expand=0, fill="x", **self.pads)
        self.form14.pack(expand=0, fill="both", **self.pads)
        self.e14.pack(expand=0, fill="x", **self.pads)
        self.form2.pack(expand=0, fill="both", **self.pads)
        self.e2.pack(expand=0, fill="x", **self.pads)
        self.form3.pack(expand=0, fill="both", **self.pads)
        self.e3.pack(expand=0, fill="x", **self.pads)
        self.form4.pack(expand=0, fill="both", **self.pads)
        self.e4.pack(expand=0, fill="x", **self.pads)
        self.form10.pack(expand=0, fill="both", **self.pads)
        self.e10.pack(expand=0, fill="x", **self.pads)
        self.form11.pack(expand=0, fill="both", **self.pads)
        self.e11.pack(expand=0, fill="x", **self.pads)
        self.form5.pack(expand=0, fill="both", **self.pads)
        self.e5.pack(expand=0, fill="x", **self.pads)
        self.form7.pack(expand=0, fill="both", **self.pads)
        self.e7.pack(expand=0, fill="x", **self.pads)
        self.form8.pack(expand=0, fill="both", **self.pads)
        self.e8.pack(expand=0, fill="x", **self.pads)
        self.form9.pack(expand=0, fill="both", **self.pads)
        self.e9.pack(expand=0, fill="x", **self.pads)

        if mode == "add":
            self.b2.config(state="disabled", disabledforeground="#87af5f")
            self.b4.config(state="normal")
            self.form12.pack(expand=0, fill="both", **self.pads)
            self.e12.pack(expand=0, fill="x", **self.pads)
            self.form13.pack(expand=0, fill="both", **self.pads)
            self.e13.pack(expand=0, fill="x", **self.pads)
            self.form14.pack(expand=0, fill="both", **self.pads)
            self.e14.pack(expand=0, fill="x", **self.pads)
            self.unset_instant_query()

        elif mode == "search":
            self.b2.config(state="normal")
            self.b4.config(state="disabled", disabledforeground="#87af5f")
            self.form10.pack_forget()
            self.e10.pack_forget()
            self.form11.pack_forget()
            self.e11.pack_forget()
            self.form12.pack_forget()
            self.e12.pack_forget()
            self.form13.pack_forget()
            self.e13.pack_forget()
            self.form14.pack_forget()
            self.e14.pack_forget()
            self.set_instant_query()

        elif mode == "update":
            self.form12.pack(expand=0, fill="both", **self.pads)
            self.e12.pack(expand=0, fill="x", **self.pads)
            self.form13.pack(expand=0, fill="both", **self.pads)
            self.e13.pack(expand=0, fill="x", **self.pads)
            self.form14.pack(expand=0, fill="both", **self.pads)
            self.e14.pack(expand=0, fill="x", **self.pads)
            self.unset_instant_query()

        self.form_button.pack(expand=0, **self.pads)

    def close_form(self):
        """Μέθοδος για κλείσιμο του μενού αναζήτησης-προσθήκης"""

        self.b2.pack(expand=1, fill="x", side="left", **self.pads)
        self.b4.pack(expand=1, fill="x", side="right", **self.pads)

        self.clear_fields()
        for i in self.sidebar_lower_frame.winfo_children():
            i.pack_forget()
        self.sidebar_lower_frame.pack_forget()

    def clear_fields(self):
        """Μέθοδος απαλοιφής των περιεχομένων των πεδίων"""

        entries = (
            self.e1,
            self.e2,
            self.e3,
            self.e4,
            self.e5,
            self.e7,
            self.e8,
            self.e9,
            self.e10,
            self.e11,
            self.e12,
            self.e13,
            self.e14,
        )

        for entry_box in entries:
            entry_box.delete(0, "end")

    def set_instant_query(self):
        self.e1.bind("<KeyRelease>", self.make_query)
        self.e2.bind("<KeyRelease>", self.make_query)
        self.e3.bind("<KeyRelease>", self.make_query)
        self.e4.bind("<KeyRelease>", self.make_query)
        self.e5.bind("<KeyRelease>", self.make_query)
        self.e7.bind("<KeyRelease>", self.make_query)
        self.e8.bind("<KeyRelease>", self.make_query)
        self.e9.bind("<KeyRelease>", self.make_query)

    def unset_instant_query(self):
        self.e1.unbind("<KeyRelease>")
        self.e2.unbind("<KeyRelease>")
        self.e3.unbind("<KeyRelease>")
        self.e4.unbind("<KeyRelease>")
        self.e5.unbind("<KeyRelease>")
        self.e7.unbind("<KeyRelease>")
        self.e8.unbind("<KeyRelease>")
        self.e9.unbind("<KeyRelease>")

    def clear_search_fields(self):
        """Μέθοδος απαλοιφής των περιεχομένων των πεδίων αναζήτησης"""

        self.clear_fields()
        self.clear_center_frame()
        self.draw_table(self.full_df)
        self.show_table()

    def make_query(self, event):
        opts = []
        for entry in zip(
            list(self.full_df.columns),
            (
                self.e1.get(),
                self.e2.get(),
                self.e3.get(),
                self.e4.get(),
                self.e5.get(),
                self.e7.get(),
                self.e8.get(),
                self.e9.get(),
            ),
        ):
            if entry[1]:
                opts.append(f'"{entry[0]}" like "%{entry[1]}%"')
        query = f'where {" and ".join(opts)}' if opts else ""
        self.search_result_df = database_functions.search_database(query)
        self.clear_center_frame()
        self.draw_table(self.search_result_df)
        self.b2.config(state="normal")
        self.b4.config(state="normal")

    def search_form(self):
        """Μέθοδος για αναζήτηση στον πίνακα"""

        self.clear_fields()
        self.form_button.config(
            text=" Καθαρισμός πεδίων ", command=self.clear_search_fields
        )

        self.b4.bind("<1>", self.open_form("search"))
        self.e1.focus()

    def add_form(self):
        """Μέθοδος για προσθήκη νέου έργου"""

        def new_entry():
            title = self.e1.get()
            department = self.e14.get()
            artist = self.e2.get()
            nationality = self.e3.get()
            gender = self.e4.get()
            begindate = self.e10.get()
            enddate = self.e11.get()
            dimensions = self.e5.get()
            date = self.e7.get()
            dateacquired = self.e8.get()
            medium = self.e9.get()
            url = self.e12.get()
            thumbnailurl = self.e13.get()

            new_entry_info = [
                title,
                department,
                artist,
                nationality,
                gender,
                begindate,
                enddate,
                dimensions,
                date,
                dateacquired,
                medium,
                url,
                thumbnailurl,
            ]

            self.full_df = database_functions.insert(new_entry_info)
            self.close_form()
            self.clear_center_frame()
            self.draw_table(self.full_df)
            self.b2.config(state="normal")
            self.select_first_table_row()

        self.clear_fields()
        self.form_button.config(text=" Προσθήκη ", command=new_entry)
        self.b2.bind("<1>", self.open_form("add"))
        self.e1.focus()

    def update_form(self):
        """Μέθοδος για ενημέρωση στοιχείων ενός έργου"""

        def update_entry():
            title = self.e1.get()
            department = self.e14.get()
            artist = self.e2.get()
            nationality = self.e3.get()
            gender = self.e4.get()
            begindate = self.e10.get()
            enddate = self.e11.get()
            dimensions = self.e5.get()
            date = self.e7.get()
            dateacquired = self.e8.get()
            medium = self.e9.get()
            url = self.e12.get()
            thumbnailurl = self.e13.get()

            update_entry_info = [
                title,
                department,
                artist,
                nationality,
                gender,
                begindate,
                enddate,
                dimensions,
                date,
                dateacquired,
                medium,
                url,
                thumbnailurl,
            ]

            update_entry_info.append(self.selected_object_id)
            self.full_df = database_functions.update(update_entry_info)

            self.close_form()
            self.clear_center_frame()
            self.draw_table(self.full_df)
            self.select_first_table_row()

        self.open_form("update")
        self.selected_database_info = database_functions.get_info_by_objectid(
            self.selected_object_id
        )

        for k, l in zip(
            (
                self.e1,
                self.e14,
                self.e2,
                self.e3,
                self.e4,
                self.e10,
                self.e11,
                self.e5,
                self.e7,
                self.e8,
                self.e9,
                self.e12,
                self.e13,
            ),
            self.selected_database_info,
        ):
            k.delete(0, "end")
            k.insert(0, str(l))

        self.form_button.config(text=" Ενημέρωση στοιχείων ", command=update_entry)
        self.e1.focus()

    def show_selected(self):

        self.clear_fields()
        for i in self.sidebar_lower_frame.winfo_children():
            i.pack_forget()
        self.selected_label.pack(expand=0, **self.pads)
        self.form_button.pack(expand=0, fill="x", side="bottom", **self.pads)
        self.update_button.pack(expand=0, fill="x", side="bottom", **self.pads)
        self.open_artist_tab.pack(expand=0, fill="x", side="bottom", **self.pads)
        self.open_artwork_tab.pack(expand=0, fill="x", side="bottom", **self.pads)
        self.show_artwork_image(where=self.sidebar_lower_frame)
        self.open_artwork_tab.config(command=self.create_artwork_tab)
        self.open_artist_tab.config(command=self.create_artist_tab)
        self.form_button.config(text=" Διαγραφή έργου ", command=self.delete)
        self.open_artwork_tab.config(state="normal")
        self.open_artist_tab.config(state="normal")
        self.update_button.config(command=self.update_form)

    def hide_selected(self):
        for i in self.sidebar_lower_frame.winfo_children():
            i.pack_forget()

    def delete(self):
        self.full_df = database_functions.delete_from_artworks(self.selected_object_id)
        self.close_form()
        self.hide_selected()

        self.clear_center_frame()
        self.open_stats_button_frame.destroy()
        self.stats_frame.destroy()
        self.show_results_frame.destroy()
        self.draw_table(self.full_df)

        self.table.bind("<ButtonRelease-1>", self.select_table_row)
        self.bind_arrow_keys(self.table, self.select_table_row)
        self.table.bind("<Return>", self.create_artwork_tab)
        self.open_artwork_tab.config(state="normal")
        self.table.unbind("<q>")
        self.select_first_table_row()

    def show_artwork_image(self, where, size=None):

        if self.selected_object_id:
            image_url = database_functions.get_artwork_image(self.selected_object_id)

            ## Δημιουργία και σχεδίαση της εικόνας του επιλεγμένου έργου
            ## Χρήση της βιβλιοθήκης urllib για τον χειρισμό του url της,
            ## αλλάζοντας το user-agent, ώστε να ζητήσουμε το url
            ## ως browser και όχι ως python script και να παρακαμφθεί το
            ## 403 error
            try:
                self.artwork_url = urllib.request.Request(
                    image_url, headers={"User-Agent": "Mozilla/5.0"}
                )

                ## Χρήση της βιβλιοθήκης io για τον χειρισμό κ την απεικόνιση
                ## της εικόνας από url, ως stream και όχι ως αρχείο από τοπικό path
                ## Αναφορά από https://stackoverflow.com/questions/55874159/python-3-tkinter-image-from-url-not-displaying
                with urllib.request.urlopen(self.artwork_url) as connection:
                    raw_data = connection.read()
                im = Image.open(io.BytesIO(raw_data))
                if size:

                    if im.width > im.height:
                        new_height = int(size[1])
                        new_width = int(im.width * (new_height / im.height))
                    elif im.width < im.height:
                        new_height = int(size[1])
                        new_width = int(im.width * (new_height / im.height))

                    new_size = (new_width, new_height)
                    im = Image.open(io.BytesIO(raw_data)).resize(
                        (new_size), Image.Resampling.LANCZOS
                    )
                else:
                    im = Image.open(io.BytesIO(raw_data))
                self.artwork = ImageTk.PhotoImage(im)
            except:
                self.artwork = ImageTk.PhotoImage(
                    Image.open("files/images/no_image.jpg")
                )

            self.artwork_label = tk.Label(
                where,
                bg="#9aa4a6",
                image=self.artwork,
            )
            self.artwork_label.image = self.artwork

            for widget in self.artwork_tab_frame.winfo_children():
                widget.pack_forget()
            self.artwork_label.pack(expand=1, **self.pads)

            if where == self.artwork_tab_frame:
                self.open_artwork_tab.config(
                    state="disabled", disabledforeground="#f4bf75"
                )

    def get_data_from_dbpedia(self, name):
        """Μέθοδος με την οποία ανακτώνται δεδομένα από την DBpedia"""

        ## Χρήση της βιβλιοθήκης sparqlwrapper για queries στην βάση DBpedia,
        ## η οποία επιστρέφει δομημένο περιεχόμενο απο τις πληροφορίες του wikipedia.
        ## Αναφορές από https://sparqlwrapper.readthedocs.io/en/latest/main.html#command-line-script και
        ## https://stackoverflow.com/questions/35775721/how-to-query-a-particular-dbpedia-resource-page-for-multiple-entities
        artist_name = "_".join(name.strip().title().split())
        sparql = SPARQLWrapper("http://dbpedia.org/sparql")
        sparql.setReturnFormat(JSON)
        query = f"""SELECT ?label ?thumbnail
        WHERE {{
            <http://dbpedia.org/resource/{artist_name}>
                dbo:abstract ?label ;
                dbo:thumbnail ?thumbnail .
            FILTER (lang(?label) = 'en')
        }}"""
        sparql.setQuery(query)
        try:
            self.abstract = sparql.query().convert()["results"]["bindings"][0]["label"][
                "value"
            ]
            # self.thumb_url = sparql.query().convert()['results']['bindings'][0]['thumbnail']['value']
            # print(abstract)
            # print(thumb_url)
        except Exception as e:
            # print(e)
            return None

        return self.abstract

    def show_artist_image(self, wikiqid=None, size=None):
        """Μέθοδος που εμφανίζει την εικόνα του καλλιτέχνη εφόσον είναι διαθέσιμη"""

        if self.selected_object_id and wikiqid:
            ## Χρήση της βιβλιοθήκης qwikidata για ανάκτηση του url της εικόνας του καλλλιτέχνη
            ## με τη βοήθεια του api των wikidata και του wikiqid (όπου υπάρχει) που παρέχεται στα αρχικά csv αρχεία
            try:
                ## Με χρήση του qwikidata
                artist_image_name = get_entity_dict_from_api(f"{wikiqid}")["claims"][
                    "P18"
                ][0]["mainsnak"]["datavalue"]["value"]
                artist_image_name = artist_image_name.replace(" ", "_")

                ## Με χρήση της βιβλιοθήκης sparqlwrapper για queries στην βάση DBpedia,
                ## η οποία επιστρέφει δομημένο περιεχόμενο απο τις πληροφορίες του wikipedia
                # image_url = self.get_data_from_dbpedia(self.ar.displayname)[1]
                # print(image_url)

                ## Σχηματισμός του url της εικόνας του καλλιτέχνη
                ## Αναφορά από https://stackoverflow.com/questions/34393884/how-to-get-image-url-property-from-wikidata-item-by-api
                hashsum = hashlib.md5(artist_image_name.encode()).hexdigest()
                image_url = f"https://upload.wikimedia.org/wikipedia/commons/{hashsum[0]}/{hashsum[:2]}/{artist_image_name}"

                ## Δημιουργία και σχεδίαση της εικόνας του επιλεγμένου έργου
                ## Χρήση της βιβλιοθήκης urllib για τον χειρισμό του url της,
                ## αλλάζοντας το user-agent, ώστε να ζητήσουμε το url
                ## ως browser και όχι ως python script και να παρακαμφθεί το
                ## 403 error
                self.artist_image_url = urllib.request.Request(
                    image_url, headers={"User-Agent": "Mozilla/5.0"}
                )

                ## Χρήση της βιβλιοθήκης io για τον χειρισμό κ την απεικόνιση
                ## της εικόνας από url, ως stream και όχι ως αρχείο από τοπικό path
                ## Αναφορά από https://stackoverflow.com/questions/55874159/python-3-tkinter-image-from-url-not-displaying
                with urllib.request.urlopen(self.artist_image_url) as connection:
                    raw_data = connection.read()
                im = Image.open(io.BytesIO(raw_data))
                if size:
                    ## Κάνουμε scale της εικόνας στις διαστάσεις του frame διατηρώντας το aspect ratio
                    ## στην περίπτωση που έχει δωθεί size
                    if im.width > im.height:
                        new_width = int(size[0])
                        new_height = int(im.height * (new_width / im.width))
                    if im.width < im.height:
                        new_height = int(size[1])
                        new_width = int(im.width * (new_height / im.height))
                    new_size = (new_width, new_height)
                    im = Image.open(io.BytesIO(raw_data)).resize(
                        (new_size), Image.Resampling.LANCZOS
                    )
                else:
                    im = Image.open(io.BytesIO(raw_data))
                self.artist_image = ImageTk.PhotoImage(im)
            except:
                self.artist_image = ImageTk.PhotoImage(
                    Image.open("files/images/no_image.jpg")
                )
        else:
            self.artist_image = ImageTk.PhotoImage(
                Image.open("files/images/no_image.jpg")
            )

        self.artist_label = tk.Label(
            self.artist_tab_frame,
            bg="#9aa4a6",
            image=self.artist_image,
        )
        self.artist_label.image = self.artist_image
        for widget in self.artist_tab_frame.winfo_children():
            widget.pack_forget()
        self.artist_label.pack(expand=1, **self.pads)
        self.open_artist_tab.config(state="disabled", disabledforeground="#f4bf75")

    def create_artwork_tab(self, event=None):
        """Μέθοδος που κατασκευάζει και παρουσιάζει την καρτέλα ενός έργου"""

        def artwork_show(event=None):
            for widget in self.artwork_tab_frame.winfo_children():
                widget.pack_forget()
            self.show_artwork_image(self.artwork_tab_frame, image_size)
            self.back_frame = tk.Frame(
                self.artwork_tab_frame,
                bg="#404040",
                width=50,
            )

            self.back_button = tk.Button(
                self.back_frame,
                text=" Επιστροφή ",
                command=self.create_artwork_tab,
                **self.button_options,
            )

            self.back_frame.pack(expand=0, side="bottom", **self.pads)
            self.back_button.pack(expand=1, side="left", **self.pads)
            self.root.unbind("<Return>")
            self.root.bind("<q>", self.create_artwork_tab)

        self.clear_center_frame()
        self.open_artwork_tab.config(state="disabled", disabledforeground="#f4bf75")
        self.open_artist_tab.config(state="normal")

        # self.hide_selected() δεν εχω αποφασισει ακομα αν θα κρυβω ή οχι το thumb οταν ανοιγει καρτελα
        self.artwork_tab_frame.config(bg="#303030")

        self.artwork_tab_frame.config(font=f"{self.font} 25 bold", fg="#87af5f")
        self.artwork_tab_frame.pack(expand=1, fill="both", **self.pads)
        self.artwork_tab_info_frame.pack(
            expand=1, fill="both", side="left", **self.pads
        )

        self.artwork_tab_info_label.pack(expand=1, fill="both", **self.pads)

        for attribute, value in vars(self.aw).items():
            if (
                attribute
                not in (
                    "url",
                    "thumbnailurl",
                    "objectid",
                    "constituentid",
                    "nationality",
                    "begindate",
                    "enddate",
                    "gender",
                )
                and value
            ):
                self.artwork_detail = tk.LabelFrame(
                    self.artwork_tab_info_label,
                    text=self.translations[attribute],
                    **self.label_options,
                )

                self.artwork_detail_info = tk.Label(
                    self.artwork_detail,
                    text=value.strip(),
                    wraplength=800,
                    **self.label_options,
                )
                self.artwork_detail.config(
                    fg="#87af5f", bg="#383838", font=f"{self.font} 12"
                )
                self.artwork_detail_info.config(
                    fg="#909090", bg="#393939", font=f"{self.font} 18 bold"
                )
                self.artwork_detail.pack(expand=1, fill="x", **self.pads)
                self.artwork_detail_info.pack(expand=1, fill="x", **self.pads)

        self.artwork_tab_frame.update()
        image_size = (
            self.artwork_tab_frame.winfo_width() * 0.9,
            self.artwork_tab_frame.winfo_height() * 0.9,
        )

        self.image_button_frame.pack(expand=0, side="bottom", **self.pads)
        self.image_button.pack(expand=1, side="left", **self.pads)

        self.image_button.config(command=artwork_show)
        self.root.bind("<Return>", artwork_show)
        self.return_button.pack(expand=1, side="left", **self.pads)

        self.root.bind("<q>", self.hide_artwork_tab)
        self.table.unbind("<KeyRelease>")
        self.table.unbind("<Return>")
        self.table.unbind("<Shift-Return>")
        self.available_artworks_names.unbind("<KeyRelease>")
        self.available_artworks_names.unbind("<Return>")
        self.available_artworks_names.unbind("<q>")

    def create_artist_tab(self, event=None):
        """Μέθοδος που κατασκευάζει και παρουσιάζει την καρτέλα ενός καλλιτέχνη"""

        def artist_show():
            for widget in self.artist_tab_frame.winfo_children():
                widget.pack_forget()
            self.show_artist_image(self.ar.wikiqid, image_size)
            self.artist_back_frame = tk.Frame(
                self.artist_tab_frame,
                bg="#404040",
                width=50,
            )

            self.artist_back_button = tk.Button(
                self.artist_back_frame,
                text=" Επιστροφή ",
                command=self.create_artist_tab,
                **self.button_options,
            )

            self.artist_back_frame.pack(expand=0, side="bottom", **self.pads)
            self.artist_back_button.pack(expand=1, side="left", **self.pads)
            self.root.bind("<q>", self.create_artist_tab)

        def listbox_selection(event):
            self.selected_object_id = (
                self.available_artworks_names.get(
                    self.available_artworks_names.curselection()
                )
                .split()[0]
                .strip("[")
                .strip("]")
            )
            self.row_values = database_functions.get_info_by_objectid(
                self.selected_object_id
            )
            self.aw = Artworks(*self.row_values)
            self.artist_info = database_functions.get_artist_info_by_constituentid(
                self.aw.constituentid
            )
            msg = f"\n\nΤίτλος\n{self.aw.title}\n\n\nΚαλλιτέχνης\n{self.aw.artist}"
            self.selected_label.config(text=msg)
            self.show_selected()

        def open_artwork_tab_from_listbox_selection(event):
            self.hide_artwork_tab()
            self.artwork_tab_frame.config(text=f"{self.aw.title} by {self.aw.artist}")
            self.create_artwork_tab()
            self.open_artwork_tab.config(state="disabled")
            self.open_artist_tab.config(state="normal")

        self.clear_center_frame()
        self.open_artist_tab.config(state="disabled", disabledforeground="#f4bf75")
        self.open_artwork_tab.config(state="normal")

        msg = f"\n\nΤίτλος\n{self.aw.title}\n\n\nΚαλλιτέχνης\n{self.aw.artist}"
        self.selected_label.config(text=msg)
        self.available_artworks_names.delete(0, "end")
        self.open_artwork_tab.config(state="normal")
        self.open_artist_tab.config(state="disabled")

        # self.hide_selected() δεν εχω αποφασισει ακομα αν θα κρυβω ή οχι το thumb οταν ανοιγει καρτελα
        self.artist_tab_frame.config(bg="#303030")
        self.artist_tab_frame.config(font=f"{self.font} 25 bold", fg="#87af5f")
        self.artist_tab_frame.pack(expand=1, fill="both", **self.pads)
        self.artist_tab_info_frame.pack(expand=1, fill="both", side="left", **self.pads)
        self.artist_tab_info_label.pack(expand=1, fill="both", **self.pads)

        for attribute, value in vars(self.ar).items():
            if (
                attribute
                not in (
                    "displayname",
                    "artistbio",
                    "constituentid",
                    "wikiqid",
                    "ulan",
                )
                and value
            ):
                self.artist_detail = tk.LabelFrame(
                    self.artist_tab_info_label,
                    text=self.translations[attribute],
                    **self.label_options,
                )

                self.artist_detail_info = tk.Label(
                    self.artist_detail,
                    text=value,
                    wraplength=800,
                    **self.label_options,
                )
                self.artist_detail.config(
                    fg="#87af5f", bg="#383838", font=f"{self.font} 12"
                )
                self.artist_detail_info.config(
                    fg="#909090", bg="#393939", font=f"{self.font} 18 bold"
                )
                self.artist_detail.pack(expand=0, fill="x", **self.pads)
                self.artist_detail_info.pack(expand=1, fill="x", **self.pads)

        self.artist_abstract.config(fg="#87af5f", bg="#383838", font=f"{self.font} 12")
        self.artist_abstract_info_label.config(
            fg="#909090",
            bg="#393939",
            font=f"{self.font} 16 bold",
            wrap="word",
            height=8,
        )

        if self.get_data_from_dbpedia(self.ar.displayname):
            self.artist_abstract_info_label.config(state="normal")
            self.artist_abstract_info_label.delete("1.0", "end")
            self.artist_abstract_info_label.insert(
                "end",
                self.get_data_from_dbpedia(self.ar.displayname).strip(),
            )
            self.artist_abstract_info_label.config(state="disabled")
            self.artist_abstract.pack(expand=1, fill="both", **self.pads)
            self.artist_abstract_info_label.pack(expand=1, fill="both", **self.pads)

        self.available_artworks.pack(expand=1, fill="both", **self.pads)
        self.available_artworks_names.pack(expand=1, fill="both", **self.pads)
        self.available_artworks_names.focus_set()
        self.vertical_scrollbar = ttk.Scrollbar(
            self.available_artworks_names,
            orient=tk.VERTICAL,
            command=self.available_artworks_names.yview,
        )
        self.available_artworks_names.config(yscroll=self.vertical_scrollbar.set)
        self.vertical_scrollbar.pack(expand=0, fill="y", **self.pads, side="right")

        self.obj_ids = database_functions.get_artworks_by_constituentid(
            self.ar.constituentid
        )

        self.available_artworks.config(
            fg="#87af5f",
            bg="#383838",
            font=f"{self.font} 12",
            text=f"Έργα του ίδιου καλλιτέχνη που είναι διαθέσιμα  -  Σύνολο: {len(self.obj_ids)}",
        )
        self.available_artworks_names.config(
            fg="#909090",
            bg="#393939",
            font=f"{self.font} 15 bold",
        )

        self.obj_ids = [t[0] for t in self.obj_ids]

        ## Εισαγωγή των υπόλοιπων έργων του καλλιτέχνη στο ListBox
        for obj_id in self.obj_ids:
            aw_info = database_functions.get_info_by_objectid(obj_id)
            selected_row = Artworks(*aw_info)
            self.available_artworks_names.insert(
                "end",
                # f"[{selected_row.objectid}]  {selected_row.title}  ({selected_row.date.strip('(').strip(')')})",
                f"[{selected_row.objectid}]  {selected_row.title},  {selected_row.date}",
            )

        self.table.unbind("<KeyRelease>")
        self.table.unbind("<Return>")
        self.table.unbind("<Shift-Return>")
        self.root.unbind("<Return>")
        self.available_artworks_names.select_set(0)
        self.bind_arrow_keys(self.available_artworks_names, listbox_selection)
        self.available_artworks_names.bind("<ButtonRelease-1>", listbox_selection)
        self.available_artworks_names.bind(
            "<Return>", open_artwork_tab_from_listbox_selection
        )

        self.root.bind("<q>", self.hide_artist_tab)

        self.artist_tab_frame.update()
        image_size = (
            self.artist_tab_frame.winfo_width() * 0.9,
            self.artist_tab_frame.winfo_height() * 0.9,
        )

        self.artist_image_button_frame.pack(expand=0, side="bottom", **self.pads)
        self.artist_image_button.pack(expand=1, side="left", **self.pads)
        self.artist_image_button.config(command=artist_show)
        self.artist_return_button.pack(expand=1, side="left", **self.pads)
        self.artist_return_button.config(command=self.hide_artist_tab)

    def clear_center_frame(self):
        """Μέθοδος που χρησιμοποιείται για καθάρισμα του center_frame από διάφορα frames που περιέχει κατά περίπτωση"""

        for widget in self.center_frame.winfo_children():
            for child in widget.winfo_children():
                child.pack_forget()
            widget.pack_forget()

        for widget in self.artist_tab_info_label.winfo_children():
            widget.pack_forget()

        for widget in self.available_artworks_names.winfo_children():
            widget.pack_forget()

        for widget in self.artwork_tab_info_label.winfo_children():
            widget.pack_forget()

    def show_table(self):

        self.open_stats_button_frame.pack(expand=0, fill="x", **self.pads)
        self.results_number.pack(expand=0, side="left", fill="x", **self.pads)
        self.open_stats_button.pack(expand=0, side="right", fill="x", **self.pads)

        self.show_results_frame.pack(expand=1, side="bottom", fill="both", **self.pads)
        self.ver_scrollbar.pack(expand=0, fill="y", side="right")
        self.hor_scrollbar.pack(expand=0, fill="x", side="bottom")
        self.table.pack(expand=1, fill="both", **self.pads)

        self.table.focus_set()
        self.available_artworks_names.unbind("<KeyRelease>")
        self.available_artworks_names.unbind("<ButtonRelease-1>")
        self.available_artworks_names.unbind("<Return>")

        self.table.bind("<ButtonRelease-1>", self.select_table_row)
        self.bind_arrow_keys(self.table, self.select_table_row)
        self.table.bind("<Return>", self.create_artwork_tab)
        self.table.bind("<Shift-Return>", self.create_artist_tab)
        self.open_artist_tab.config(state="normal")
        self.open_artwork_tab.config(state="normal")
        self.root.unbind("<q>")
        self.root.unbind("<Return>")

    def hide_artwork_tab(self, event=None):

        self.clear_center_frame()
        self.show_table()

    def hide_artist_tab(self, event=None):

        self.clear_center_frame()
        self.show_table()

    def select_random_artwork(self):
        """Μέθοδος που ανοίγει ένα τυχαία επιλεγμένο έργο"""

        objectids = database_functions.all_objectids()
        self.selected_object_id = choice(objectids)[0]

        self.row_values = database_functions.get_info_by_objectid(
            self.selected_object_id
        )

        self.aw = Artworks(*self.row_values)
        self.artist_info = database_functions.get_artist_info_by_constituentid(
            self.aw.constituentid
        )
        self.ar = Artists(*self.artist_info)
        msg = f"\n\nΤίτλος\n{self.aw.title}\n\n\nΚαλλιτέχνης\n{self.aw.artist}"
        self.selected_label.config(text=msg)
        self.show_selected()
        self.artwork_tab_frame.config(text=f"{self.aw.title} by {self.aw.artist}")
        self.artist_tab_frame.config(text=f"{self.aw.artist}")
        self.create_artwork_tab()
        self.open_artwork_tab.config(state="disabled")
        self.open_artist_tab.config(state="normal")


if __name__ == "__main__":

    try:
        database_functions.load_database()
        root = tk.Tk()
        MomaGuiApp(root)
        root.mainloop()
    except Exception as e:
        print(e)
