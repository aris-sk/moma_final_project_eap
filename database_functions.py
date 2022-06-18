#!/usr/bin/env python3

import pandas as pd
import sqlite3
from sqlite3 import Error
from wget import download
import os, time


def load_database():
    """Σύνδεση στη βάση δεδομένων (δημιουργία αν δεν υπάρχει) και εισαγωγή των dataframes"""

    if not os.path.exists("mydatabase.db") or os.path.getsize("mydatabase.db") == 0:
        try:
            ## Κατέβασμα των αρχείων csv με τα δεδομένα από το github
            location = "files"
            download("https://media.githubusercontent.com/media/MuseumofModernArt/collection/master/Artists.csv", location)
            download("https://media.githubusercontent.com/media/MuseumofModernArt/collection/master/Artworks.csv", location)

            ## Αναμονή για ολοκλήρωση των λήψεων
            while not os.path.exists("files/Artists.csv"):
                time.sleep(1)
            while not os.path.exists("files/Artworks.csv"):
                time.sleep(1)

            ## Φόρτωση των csv αρχείων σε dataframes       
            df_artists = pd.read_csv("files/Artists.csv")
            df_artworks = pd.read_csv("files/Artworks.csv")

            ## Κατασκευή των πινάκων της βάσης δεδομένων με sql script
            with open("files/create_tables.sql", "r") as f:
                sql_script = f.read()

            connection = sqlite3.connect("mydatabase.db")
            cursor = connection.cursor()
            cursor.executescript(sql_script)

            ## Θα κρατήσουμε τα έργα των κατηγοριών "Painting & Sculpture" και "Media and Performance"
            df_artworks = df_artworks.loc[
                (df_artworks["Department"] == "Painting & Sculpture")
                | (df_artworks["Department"] == "Media and Performance")
            ]

            ## Εισαγωγή των στοιχείων των dataframes ως tables στη βάση δεδομένων
            df_artists.to_sql("artists", connection, if_exists="append", index=False)
            df_artworks.to_sql("artworks", connection, if_exists="append", index=False)

            cursor.close()
            connection.close()

        except (Exception, Error) as error:
            print(f"\nΣφάλμα κατά την δημιουργία της βάσης δεδομένων\n{error}\n")


def search_database(query_options=None):
    """Συνάρτηση για την αναζήτηση στη βάση δεδομένων"""

    if not query_options:
        query_options = ""
    connection = sqlite3.connect("mydatabase.db")
    query = f'SELECT title as ΤΊΤΛΟΣ, artist as ΚΑΛΛΙΤΈΧΝΗΣ, Nationality as ΕΘΝΙΚΌΤΗΤΑ, gender as ΦΎΛΟ, dimensions as "ΔΙΑΣΤΆΣΕΙΣ ή ΔΙΆΡΚΕΙΑ", date as "ΧΡΟΝΟΛΟΓΊΑ ΈΡΓΟΥ", DateAcquired as "ΗΜΕΡΟΜΗΝΊΑ ΑΠΌΚΤΗΣΗΣ", Medium as "ΜΈΣΟ ΈΡΓΟΥ", "ObjectID"  FROM  artworks  {query_options}'
    sql_query = pd.read_sql_query(query, connection)
    df = pd.DataFrame(sql_query, index=None)
    connection.close()
    return df


def get_table_columns(table):
    """Συνάρτηση που επιστρέφει λίστα των στηλών του πίνακα με τα έργα"""

    connection = sqlite3.connect("mydatabase.db")
    query = f"select * from {table}"
    sql_query = pd.read_sql_query(query, connection)
    df = pd.DataFrame(sql_query, index=None)
    return list(df.columns)


def insert(new_entry_info):
    """Συνάρτηση για την προσθήκη έργου"""

    ## Εξετάζουμε αν υπάρχει ήδη καταχώρηση έργου με τον ίδιο καλλιτέχνη με το έργο
    ## που προστίθεται
    add_new_artist = False
    new_entry_info = list(new_entry_info)

    ## Μετατρέπω τα strings της λίστας σε μόρφή title, για ομοιομορφία με τα καταχωρημένα
    for index, element in enumerate(new_entry_info):
        if isinstance(element, str):
            new_entry_info[index] = element.title()
    artist_name = new_entry_info[2]

    connection = sqlite3.connect("mydatabase.db")
    cursor = connection.cursor()
    if_exists_query = "SELECT ConstituentID FROM artworks WHERE artist=?"
    cursor.execute(if_exists_query, (artist_name,))
    con_id = cursor.fetchone()

    ## Αν έχει κι άλλα έργα ο ίδιος καλλιτέχνης τότε αποδίδεται στο έργο το ίδιο ConstituentID
    if con_id:
        new_entry_info.append(con_id[0])
        insert_statement = "INSERT INTO artworks (Title, Department, Artist, Nationality, Gender, BeginDate, EndDate, Dimensions, Date, DateAcquired, Medium, URL, ThumbnailURL, ConstituentID) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
        cursor.execute(insert_statement, new_entry_info)

        ## Ενημέρωση στοιχείων καλλιτέχνη που είναι κοινά για όλα τα έργα του
        updates = new_entry_info
        update_common_info = [
            updates[2].title(),
            updates[3].title(),
            updates[4].title(),
            updates[5],
            updates[6],
            updates[-1],
        ]

        ## Η ενημέρωση θα γίνεται μόνο εφόσον έχουν δοθεί τιμές στα αντίστοιχα πεδία,
        ## ώστε να μην διαγραφούν τυχόν συμπληρωμένες τιμές στα ίδια πεδία των άλλων έργων
        ## του καλλιτέχνη, λόγω παράλλειψης ή άλλου λόγου
        for u, f in zip(
            update_common_info[:-1],
            ("Artist", "Nationality", "Gender", "BeginDate", "EndDate"),
        ):
            if u != "":
                update_rest_statement = (
                    f'UPDATE artworks SET {f}="{u}" WHERE ConstituentID={con_id[0]}'
                )
                cursor.execute(update_rest_statement)

        ## Ενημέρωση και των στοιχείων του πίνακα artists με αντίστοιχα στοιχεία που υπάρχουν
        ## και στον πίνακα artworks και έχουν ενημερωθεί
        update_artist_info = (
            [update_common_info[0]]
            + [
                f"{update_common_info[1]}, {update_common_info[3]}-{update_common_info[4]}"
            ]
            + update_common_info[1:]
        )

        ## Ομοίως και εδώ θα ενημερωθούν τα στοιχεία στον πίνακα artists μόνο αν έχουν δοθεί τιμές,
        ## ώστε να μη διαγραφούν στοιχεία που υπάρχουν από παράλλειψη
        for u, f in zip(
            update_artist_info[:-1],
            (
                "DisplayName",
                "ArtistBio",
                "Nationality",
                "Gender",
                "BeginDate",
                "EndDate",
            ),
        ):
            if u != "":
                update_artists_table_statement = (
                    f'UPDATE artists SET {f}="{u}" WHERE ConstituentID={con_id[0]}'
                )
                cursor.execute(update_artists_table_statement)

    ## Αλλιώς το ConstituentID που αποδίδεται στο έργο είναι το αμέσως επόμενο σε αύξουσα σειρά
    else:
        max_con_id_query = "SELECT MAX(ConstituentID) FROM artists"
        cursor.execute(max_con_id_query)
        max_con_id = cursor.fetchone()
        new_entry_info.append(max_con_id[0] + 1)
        insert_statement = "INSERT INTO artworks (Title, Department, Artist, Nationality, Gender, BeginDate, EndDate, Dimensions, Date, DateAcquired, Medium, URL, ThumbnailURL, ConstituentID) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
        cursor.execute(insert_statement, new_entry_info)
        add_new_artist = True

    connection.commit()
    cursor.close()
    connection.close()
    new_df = search_database()

    ## Αν δεν υπάρχει καθόλου ο καλλιτέχνης προστίθεται και στον πίνακα artists
    if add_new_artist:
        insert_new_artist_in_artists(new_entry_info)
    return new_df


def insert_new_artist_in_artists(new_entry_info):
    """Συνάρτηση που καλείται από την insert και προσθέτει στον πίνακα artists καλλιτέχνη
    που δεν υπάρχει καθόλου στην βάση δεδομένων"""

    connection = sqlite3.connect("mydatabase.db")
    cursor = connection.cursor()

    ## Επιπλέον προσθέτουμε και στον πίνακα artists όσα στοιχεία έχουν δoθεί που υπάρχουν και σε αυτόν
    artists_insert_statement = "INSERT INTO artists (DisplayName, ArtistBio, Nationality, Gender, BeginDate, EndDate, ConstituentID) VALUES (?, ?, ?, ?, ?, ?, ?)"
    artist_entries = (
        new_entry_info[2],
        f"{new_entry_info[3]}, {new_entry_info[5]}-{new_entry_info[6]}",
        new_entry_info[3],
        new_entry_info[4],
        new_entry_info[5],
        new_entry_info[6],
        new_entry_info[-1],
    )
    cursor.execute(artists_insert_statement, artist_entries)
    connection.commit()
    cursor.close()
    connection.close()


def get_info_by_objectid(objectid):
    """Συνάρτηση για την λήψη στοιχείων ενός έργου από το objectid του"""

    connection = sqlite3.connect("mydatabase.db")
    cursor = connection.cursor()
    query_statement = "SELECT Title, Department, Artist, Nationality, Gender, BeginDate, EndDate, Dimensions, Date, DateAcquired, Medium, URL, ThumbnailURL, CreditLine, ObjectID, ConstituentID FROM artworks WHERE ObjectID=?"
    cursor.execute(query_statement, (objectid,))
    info = cursor.fetchone()
    cursor.close()
    connection.close()
    return info


def all_objectids():
    """Συνάρτηση για την λήψη των objectids των έργων"""

    connection = sqlite3.connect("mydatabase.db")
    cursor = connection.cursor()
    query_statement = "SELECT ObjectID FROM artworks"
    cursor.execute(query_statement)
    objectids = cursor.fetchall()
    cursor.close()
    connection.close()
    return objectids


def get_artist_info_by_constituentid(constituentid):
    """Συνάρτηση για την λήψη στοιχείων ενός καλλιτέχνη από το constituentid"""

    connection = sqlite3.connect("mydatabase.db")
    cursor = connection.cursor()
    query_statement = "SELECT * FROM artists WHERE ConstituentID=?"
    cursor.execute(query_statement, (constituentid,))
    info = cursor.fetchone()
    cursor.close()
    connection.close()
    return info


def get_artworks_by_constituentid(constituentid):
    """Συνάρτηση για την λήψη των ενός καλλιτέχνη από το constituentid"""

    connection = sqlite3.connect("mydatabase.db")
    cursor = connection.cursor()
    query_statement = "SELECT ObjectID FROM artworks WHERE ConstituentID=?"
    cursor.execute(query_statement, (constituentid,))
    titles_objectids = cursor.fetchall()
    cursor.close()
    connection.close()
    return titles_objectids


def update(updates):
    """Συνάρτηση για την ενημέρωση στοιχείων ενός έργου"""

    ## Θα ενημερώσουμε όλα τα έργα με στοιχεία που είναι κοινά και για αυτά,
    ## καθώς επίσης και στοιχεία που αναφέρονται και στον πίνακα του καλλιτέχνη
    connection = sqlite3.connect("mydatabase.db")
    cursor = connection.cursor()

    ## Αναζητούμε το ConstituentID του καλλιτέχνη βάσει του ObjectID του έργου
    con_id = get_info_by_objectid(updates[-1])[-1]

    ## Ενημέρωση στοιχείων του επιλεγμένου έργου
    update_statement = "UPDATE artworks SET Title=?, Department=?, Artist=?, Nationality=?, Gender=?, BeginDate=?, EndDate=?, Dimensions=?, Date=?, DateAcquired=?, Medium=?, URL=?, ThumbnailURL=? WHERE ObjectID=?"
    cursor.execute(update_statement, updates)

    ## Ενημέρωση στοιχείων καλλιτέχνη που είναι κοινά για όλα τα έργα του
    update_common_info = [
        updates[2].title(),
        updates[3].title(),
        updates[4].title(),
        updates[5],
        updates[6],
        con_id,
    ]

    update_rest_statement = "UPDATE artworks SET Artist=?, Nationality=?, Gender=?, BeginDate=?, EndDate=? WHERE ConstituentID=?"
    cursor.execute(update_rest_statement, update_common_info)

    ## Ενημέρωση και των στοιχείων του πίνακα artists με αντίστοιχα στοιχεία που υπάρχουν
    ## και στον πίνακα artworks και έχουν ενημερωθεί
    update_artist_info = (
        [update_common_info[0]]
        + [f"{update_common_info[1]}, {update_common_info[3]}-{update_common_info[4]}"]
        + update_common_info[1:]
    )
    update_artists_table_statement = "UPDATE artists SET DisplayName=?, ArtistBio=?, Nationality=?, Gender=?, BeginDate=?, EndDate=? WHERE ConstituentID=?"
    cursor.execute(update_artists_table_statement, update_artist_info)

    connection.commit()
    cursor.close()
    connection.close()

    new_df = search_database()
    return new_df


def delete_from_artworks(objectid):
    """Συνάρτηση για την διαγραφή έργου"""

    connection = sqlite3.connect("mydatabase.db")
    cursor = connection.cursor()
    delete_statement = "DELETE from artworks WHERE ObjectID=?"
    cursor.execute(delete_statement, (objectid,))
    connection.commit()
    cursor.close()
    connection.close()
    new_df = search_database()
    return new_df


def get_artwork_image(objectid):
    """Συνάρτηση που επιστρέφει το url της εικόνας του έργου, αν υπάρχει"""

    connection = sqlite3.connect("mydatabase.db")
    cursor = connection.cursor()
    select_statement = "SELECT ThumbnailURL from artworks WHERE ObjectID=?"
    cursor.execute(select_statement, (objectid,))
    image_url = cursor.fetchone()[0]
    cursor.close()
    connection.close()
    return image_url
