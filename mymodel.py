import sqlite3
import hashlib
DB_NAME = "db new.db" 

def get_connection():
    con = sqlite3.connect(DB_NAME)
    con.execute("PRAGMA foreign_keys = ON;")
    return con

#Λειτουργίες δημοσιεύσεων

def get_all_publications(): #προβολή όλων των δημοσιεύσεων που υπάρχουν στη βάση
    publications=[]
    with get_connection() as con:
        cur=con.cursor()
        cur.execute("""
            SELECT DOI, Titlos, Glossa, Imer_prosthikis, Perilipsi, URL
            FROM DIMOSIEYSI
            ORDER BY Imer_prosthikis DESC;
        """)
        colnames=[d[0] for d in cur.description]
        for row in cur.fetchall():
            publications.append(dict(zip(colnames, row)))
    return publications

def insert_publication(doi, title, language, summary, url): #εισαγωγή δημοσίευσης
    with get_connection() as con:
        cur=con.cursor()
        try:
            cur.execute("""
                INSERT INTO DIMOSIEYSI (DOI, Titlos, Glossa, Imer_prosthikis, Perilipsi, URL)
                VALUES (?, ?, ?, DATE('now'), ?, ?);
            """, (doi, title, language, summary, url))
            con.commit()
        except sqlite3.IntegrityError as e:
            raise ValueError(f"Αποτυχία εισαγωγής: Το DOI '{doi}' υπάρχει ήδη.") from e

def delete_publication(doi): #διαγραφή δημοσίευσης
    with get_connection() as con: 
        cur = con.cursor()
        try:
            cur.execute("DELETE FROM DIMOSIEYSI WHERE DOI=?;", (doi,))
            if cur.rowcount==0:
                raise LookupError("Δεν βρέθηκε δημοσίευση με αυτό το DOI")
            con.commit()
        except sqlite3.IntegrityError as e:
            raise RuntimeError("Δεν είναι δυνατή η διαγραφή: υπάρχουν σχετικές αναφορές.") from e

def get_pub_type(doi): #επιστρέφει τον τύπο της δημοσίευσης
    with get_connection() as con:
        cur=con.cursor()
        cur.execute("SELECT 1 FROM ARTHRO_SE_PERIODIKO WHERE DOI_dimosieysis=?", (doi,))
        if cur.fetchone():
            return "Περιοδικό"
        cur.execute("SELECT 1 FROM ARTHRO_SE_SYNEDRIO WHERE DOI_dimosieysis=?", (doi,))
        if cur.fetchone():
            return "Συνέδριο"
        return "Άγνωστο"
    
def get_detailed_pub_info(doi, pub_type): #επιστρέφει λεπτομέρειες ανάλογα με τον τύπο της δημοσίευσης
    with get_connection() as con:
        cur=con.cursor()
        if pub_type=="Περιοδικό":
            cur.execute("SELECT ISSN, Imer_dimosieysis, Teyxos, Tomos, Selides_periodikou FROM ARTHRO_SE_PERIODIKO WHERE DOI_dimosieysis=?", (doi,))
        elif pub_type=="Συνέδριο":
            cur.execute("SELECT ISBN, Onoma_synedriou, Imer_dieksagogis, Topos_dieksagogis FROM ARTHRO_SE_SYNEDRIO WHERE DOI_dimosieysis=?", (doi,))
        row=cur.fetchone()
        if row:
            colnames=[d[0] for d in cur.description]
            return dict(zip(colnames, row))
        return {}

#Λειτουργίες συγγραφέων

def get_all_authors(): #προβολή όλων των συγγραφέων
    authors=[]
    with get_connection() as con:
        cur=con.cursor()
        cur.execute("""
            SELECT id_syggrafea, Onomateponymo
            FROM SYGGRAFEAS
            ORDER BY Onomateponymo;
        """)
        colnames=[d[0] for d in cur.description]
        for row in cur.fetchall():
            authors.append(dict(zip(colnames, row)))
    return authors

def insert_author(fullname): #εισαγωγή συγγραφέα
    with get_connection() as con:
        cur=con.cursor()
        try:
            cur.execute("""
                INSERT INTO SYGGRAFEAS (Onomateponymo)
                VALUES (?);
            """, (fullname,))
            con.commit()
        except sqlite3.IntegrityError as e:
            raise ValueError("Αποτυχία εισαγωγής συγγραφέα. Το όνομα υπάρχει ήδη.")

def get_authors_from_publication(doi): #συγγραφείς μιας δημοσίευσης
    authors_pub=[]
    with get_connection() as con:
        cur=con.cursor()
        cur.execute("""
            SELECT Onomateponymo FROM SYSXETISI_SYGGR_DIMOS_IDR AS s1
            JOIN SYGGRAFEAS AS s2 ON s1.id_syggrafea=s2.id_syggrafea
            WHERE s1.DOI_dimosieysis=?;
        """, (doi,))
        colnames=[d[0] for d in cur.description]
        for row in cur.fetchall():
            authors_pub.append(dict(zip(colnames, row)))
    return authors_pub

def link_author_to_publication(author_id, doi, id_idrymatos): #συσχέτιση συγγραφέα με δημοσίευση
    with get_connection() as con:
        cur = con.cursor()
        try:
            cur.execute("""
                INSERT INTO SYSXETISI_SYGGR_DIMOS_IDR (id_syggrafea, DOI_dimosieysis, id_idrymatos)
                VALUES (?, ?, ?);
            """, (author_id, doi, id_idrymatos))
            con.commit()
        except sqlite3.IntegrityError as e:
            pass #αν υπάρχει ήδη η σύνδεση
        except Exception as e:
            raise RuntimeError(f"Σφάλμα σύνδεσης συγγραφέα με δημοσίευση: {e}") from e

def get_all_institutions(): #προβολή όλων των ιδρυμάτων που υπάρχουν στη βάση
    institutions=[]
    with get_connection() as con:
        cur=con.cursor()
        cur.execute("""
            SELECT id_idrymatos, Onoma, Dieythinsi
            FROM IDRYMA
            ORDER BY id_idrymatos;
        """)
        colnames=[d[0] for d in cur.description]
        for row in cur.fetchall():
            institutions.append(dict(zip(colnames, row)))
    return institutions

#Λειτουργίες λέξεων-κλειδιών

def get_keywords_for_publication(doi): #επιστρέφει λέξεις-κλειδιά μιας δημοσίευσης
    keywords=[]
    with get_connection() as con:
        cur=con.cursor()
        cur.execute("""
        SELECT lk.keyword FROM DIMOS_EXEI_LEKSEIS_KLEIDIA AS d
        JOIN LEKSI_KLEIDI AS lk ON d.id_leksis=s2.lk_keyword_id
        WHERE d.DOI_dimosieysis=?;
    """, (doi,))
    colnames=[d[0] for d in cur.description]
    for row in cur.fetchall():
        keywords.append(dict(zip(colnames, row)))
    return keywords

def get_keyword_id(keyword):   #επιστρέφει το id μιας λέξης-κλειδί
    keywordID=[]
    with get_connection() as con:
        cur=con.cursor()
        cur.execute("""
        SELECT keyword_id FROM LEKSI_KLEIDI
        WHERE keyword=?;
    """, (keyword,))
    colnames=[d[0] for d in cur.description]
    for row in cur.fetchall():
        keywordID.append(dict(zip(colnames, row)))
    return keywordID

def insert_new_keyword(keyword): #εισαγωγή λέξης-κλειδιού στη βάση
    with get_connection() as con:
        cur=con.cursor()
        try:
            cur.execute("INSERT INTO LEKSI_KLEIDI (keyword) VALUES (?)", (keyword,))
            con.commit()
            return cur.lastrowid
        except sqlite3.IntegrityError:
            return get_keyword_id(keyword)
        except Exception as e:
            raise RuntimeError(f"Σφάλμα εισαγωγής λέξης-κλειδιού: {e}") from e
        
def insert_keyword(doi, keyword): #προσθήκη λέξης-κλειδί σε δημοσίευση, αποθηκεύει τη λέξη αν δεν υπάρχει
    keyword=keyword.strip()
    if not keyword:
        return
    keyword_id=insert_new_keyword(keyword)
    if keyword_id is None:
        keyword_id=insert_new_keyword(keyword)

    with get_connection() as con:
        cur=con.cursor()
        try:
            cur.execute("""
                        INSERT INTO DIMOS_EXEI_LEKSEIS_KLEIDIA (DOI_dimosieysis, id_leksis)
                        VALUES (?, ?);
                        """, (doi, keyword_id))
            con.commit()
        except sqlite3.IntegrityError:
            pass #η σύνδεση υπάρχει ήδη
        except Exception as e:
             raise RuntimeError(f"Σφάλμα σύνδεσης λέξης-κλειδί με δημοσίευση: {e}") from e
        
#Λειτουργίες αναζήτησης/φιλτραρίσματος

def search_publications(word): #Αναζήτηση δημοσίευσης βάσει τίτλου ή DOI
    word_pattern=f"%{word}%"
    with get_connection() as con:
        cur=con.cursor()
        cur.execute("""
                    SELECT DISTINCT DOI, Titlos, Glossa, Imer_prosthikis, Perilipsi, URL
                    FROM DIMOSIEYSI WHERE Titlos LIKE ? OR DOI LIKE ? ORDER BY Titlos;""", (word_pattern, word_pattern))
        row=cur.fetchall()
        if not row:
            return None
        colnames=[d[0] for d in cur.description]
        return dict(zip(colnames, row))
    
def search_authors(name): #Αναζήτηση συγγραφέα με βάση ονοματεπώνυμο
    word_pattern=f"%{name}%"
    with get_connection() as con:
        cur=con.cursor()
        cur.execute("""
                    SELECT id_syggrafea, Onomateponymo
                    FROM SYGGRAFEAS WHERE Onomateponymo LIKE ? ORDER BY Onomateponymo;""", (word_pattern,))
        row=cur.fetchall()
        if not row:
            return None
        colnames=[d[0] for d in cur.description]
        return dict(zip(colnames, row))

def get_pubs_by_author(author_id): #επιστρέφει δημοσιεύσεις ενός συγγραφέα
    with get_connection() as con:
        cur=con.cursor()
        cur.execute("""
            SELECT D.DOI, D.Titlos, D.Glossa, D.Imer_prosthikis, D.Perilipsi, D.URL
            FROM DIMOSIEYSI AS D JOIN SYSXETISI_SYGGR_DIMOS_IDR AS S
            ON D.DOI=S.DOI_dimosieysis WHERE id_syggrafea=?
            ORDER BY D.Imer_prosthikis DESC;
                    """, (author_id,))
        row=cur.fetchall()
        if not row:
            return None
        colnames=[d[0] for d in cur.description]
        return dict(zip(colnames, row))
    
def update_pub_title(doi, new_title): #τροποποίηση τίτλου δημοσίευσης
    with get_connection() as con:
        cur=con.cursor()
        cur.execute("""
            UPDATE DIMOSIEYSI 
            SET Titlos=? 
            WHERE DOI=?;
            """, (new_title, doi))
        if cur.rowcount==0:
            raise LookupError("Δεν βρέθηκε δημοσίευση με αυτό το DOI")
        con.commit()

def update_username(old_username, new_username): #τροποποίηση username
    with get_connection() as con:
        cur=con.cursor()
        try:
            cur.execute("SELECT Username FROM XRHSTHS WHERE Username=?", (new_username,))
            if cur.fetchone():
                raise ValueError("Το νέο username χρησιμοποιείται ήδη από άλλο χρήστη")
            cur.execute("""
                UPDATE XRHSTHS 
                SET Username=? 
                WHERE Username=?;
                """, (new_username, old_username))
            con.commit()
            return True
        except sqlite3.Error as e:
            print(f"Σφάλμα κατά την αλλαγή username: {e}")
            con.rollback()
            return False
        except ValueError as e:
            print(e)
            return False
    
#Λειτουργίες σχολίων

def get_comments_by_pub(doi): #επιστρέφει τα σχόλια μιας δημοσίευσης
    with get_connection() as con:
        cur=con.cursor()
        cur.execute("""
            SELECT S.id_sxoliou, S.Periexomeno, S.Imer_dimiourgias
            FROM SXOLIO AS S JOIN PROSTHIKI_SXOLIOU_SE_DIMOSIEYSI AS P
            ON S.id_sxoliou=P.id_sxoliou
            WHERE P.DOI_dimosieysis=?
            ORDER BY D.Imer_dimiourgias DESC;
                    """, (doi,))
        row=cur.fetchall()
        if not row:
            return None
        colnames=[d[0] for d in cur.description]
        return dict(zip(colnames, row))
    
def insert_comment_to_pub(doi, username, text): #προσθήκη σχολίου σε δημοσίευση
    with get_connection() as con:
        cur=con.cursor()
        try:
            cur.execute("""
                INSERT INTO SXOLIO (Periexomeno, Imer_dimiourgias)
                VALUES (?, DATE('now'));
            """, (text,))
            last_comment_id=cur.lastrowid
            cur.execute("""
                INSERT INTO PROSTHIKI_SXOLIOU_SE_DIMOSIEYSI (id_sxoliou, Username, DOI_dimosieysis
                VALUES (?, ?, ?);
                        """, (last_comment_id, username, doi))
            con.commit()
        except sqlite3.IntegrityError as e:
            raise ValueError("Αποτυχία εισαγωγής σχολίου.")
            con.rollback() #ακύρωση αλλαγών σε περίπτωση σφάλματος

def delete_comment(comment_id, username): #διαγραφή σχολίου
    with get_connection() as con:
        cur=con.cursor()
        try:
            #διαγράφω πρώτα τις συσχετίσεις
            cur.execute("""
                DELETE FROM PROSTHIKI_SXOLIOU_SE_DIMOSIEYSI
                WHERE id_sxoliou=?;
                """, (comment_id,))
            #διαγραφή σχολίου
            cur.execute("""
                DELETE FROM SXOLIO
                WHERE id_sxoliou=? AND Username=?;
                """, (comment_id, username))
            if cur.rowcount==0:
                raise LookupError("Δεν βρέθηκε το σχόλιο")
            con.commit()
            return True
        except sqlite3.Error as e:
            print(f"Σφάλμα κατά τη διαγραφή του σχολίου: {e}")
            con.rollback() #ακύρωση αλλαγών σε περίπτωση σφάλματος
            return False
      
#Λειτουργίες φακέλων

def create_folder(name, username, parent_id, size=0): #δημιουργία φακέλου
    with get_connection() as con:
        cur=con.cursor()
        try:
            cur.execute("""
                INSERT INTO FAKELOS (id_kyriou_fakelou, Onoma, Megethos, Username)
                VALUES (?, ?, ?, ?);
                """, (parent_id, name, size, username))
            con.commit()
            return cur.lastrowid
        except sqlite3.Error as e:
            print(f"Σφάλμα κατά τη δημιουργία φακέλου: {e}")
            return None

def add_pub_to_folder(doi, folder_id, username): #προσθήκη δημοσίευσης σε φάκελο
    with get_connection() as con:
        cur=con.cursor()
        try:
            cur.execute("""
                INSERT INTO XRHSTHS_APOTHIK_DIMOS_SE_FAKELO (Username, DOI_dim, id_fakelou)
                VALUES (?, ?, ?);
                """, (username, doi, folder_id))
            con.commit()
            return True
        except sqlite3.Error as e:
            print(f"Σφάλμα κατά την αποθήκευση στον φάκελο: {e}")
            return False
                
def get_user_folders(username): #επιστρέφει τους φακέλους ενός χρήστη
    with get_connection() as con:
        cur=con.cursor()
        cur.execute("""
            SELECT id_fakelou, id_kyriou_fakelou, Onoma, Megethos
            FROM FAKELOS 
            WHERE Username=?;
            """, (username,))
        row=cur.fetchall()
        if not row:
            return []
        colnames=[d[0] for d in cur.description]
        return dict(zip(colnames, row))

def delete_folder(folder_id, username): #διαγραφή φακέλου
    with get_connection() as con:
        cur=con.cursor()
        try:
            #διαγράφω πρώτα τις συσχετίσεις
            cur.execute("""
                DELETE FROM XRHSTHS_APOTHIK_DIMOS_SE_FAKELO
                WHERE id_fakelou=? AND Username=?;
                """, (folder_id, username))
            #διαγραφή φακέλου
            cur.execute("""
                DELETE FROM FAKELOS
                WHERE id_fakelou=? AND Username=?;
                """, (folder_id, username))
            if cur.rowcount==0:
                raise LookupError("Δεν βρέθηκε ο φάκελος")
            con.commit()
            return True
        except sqlite3.Error as e:
            print(f"Σφάλμα κατά τη διαγραφή του φακέλου: {e}")
            con.rollback() #ακύρωση αλλαγών σε περίπτωση σφάλματος
            return False

#Λειτουργίες χρηστών

def hash_password(password): #επιστρέφει το hash του κωδικού
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def new_user(username, email, fullname, password): #εγγραφή νέου χρήστη
    hashed_password=hash_password(password)
    with get_connection() as con:
        cur=con.cursor()
        try:
            cur.execute("""
                INSERT INTO XRHSTHS (Username, email, Onomateponymo, Password)
                VALUES (?, ?, ?, ?);
                """, (username, email, fullname, hashed_password))
            con.commit()
            return True
        except sqlite3.IntergityError as e:
            if "Username" in str(e):
                raise ValueError("Το username χρησιμοποιείται ήδη") from e
            if "email" in str(e):
                raise ValueError("Το email χρησιμοποιείται ήδη") from e
            raise ValueError("Αποτυχία εγγραφής χρήστη") from e

def get_user_by_username(username): #επιστρέφει τα στοιχεία χρήστη
    with get_connection() as con:
        cur=con.cursor()
        cur.execute("""
            SELECT Username, email, Onomateponymo, Password
            FROM XRHSTHS 
            WHERE Username=?;
            """, (username,))
        row=cur.fetchone()
        if not row:
            return None
        colnames=[d[0] for d in cur.description]
        return dict(zip(colnames, row))

def verify_user(username, password): #επαλήθευση χρήστη
    user=get_user_by_username(username)
    if not user:
        return None
    hashed_input=hash_password(password)
    if user['Password']==hashed_input: #συγκρίνει τον hashed κωδικό που δίνει ο χρήστης με τον αποθηκευμένο
        del user['Password'] #αφαιρώ τον κωδικό πριν επιστρέψω τα στοιχεία του χρήστη
        return user
    return None

#def get_user_by_username(username): 
    """Επιστρέφει τα στοιχεία χρήστη συμπεριλαμβανομένου του ρόλου."""
    with get_connection() as con:
        cur = con.cursor()
        cur.execute("""
            SELECT Username, email, Onomateponymo, Password, is_admin
            FROM XRHSTHS 
            WHERE Username = ?;
        """, (username,))
        row = cur.fetchone()
        if not row:
            return None
        colnames = [d[0] for d in cur.description]
        return dict(zip(colnames, row))

#def is_admin(username):
    """Ελέγχει αν ένας χρήστης είναι διαχειριστής."""
    user = get_user_by_username(username)
    return user is not None and user.get('is_admin') == 1