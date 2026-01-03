from mymodel import (get_all_publications, get_folder_publications_details, insert_publication, delete_publication,
                     get_pub_type, get_detailed_pub_info, get_all_authors, insert_author,
                     get_authors_from_publication, link_author_to_publication, get_all_institutions,
                     get_keywords_for_publication, get_keyword_id, insert_new_keyword, insert_keyword,
                     search_publications, search_authors, get_pubs_by_author, get_pubs_by_keyword, update_pub_title, update_username,
                     get_folder_parent_id, is_in_general_subtree, get_comments_by_pub_and_user, insert_comment_to_pub, delete_comment, get_or_create_folder,
                     add_pub_to_folder, remove_pub_from_folder, get_user_folders, get_subfolders, 
                     delete_folder, hash_password, new_user, get_user_by_username, verify_user, is_admin)

from view import (show_message, show_error, show_menu, show_publications_list, show_publication_details, print_folder_subtree)


starting_options = {
    "1": "Σύνδεση",
    "2": "Εγγραφή"
}

user_options = {
    "1": "Εμφάνιση αποθηκευμένων δημοσιεύσεων και φακέλων",
    "2": "Εμφάνιση φακέλου",
    "3": "Προσθήκη δημοσίευσης",
    "4": "Διαγραφή δημοσίευσης",
    "5": "Δημιουργία φακέλου",
    "6": "Διαγραφή φακέλου",
    "7": "Δημιουργία σχολίου",
    "8": "Διαγραφή σχολίου",
    "9": "Προβολή σχολίων μιας δημοσίευσης",
    "10": "Αναζήτηση δημοσίευσης με βάση τίτλο ή DOI",
    "11": "Αναζήτηση δημοσίευσης με βάση συγγραφέα",
    "12": "Αναζήτηση δημοσίευσης με βάση λέξη-κλειδί"

}

admin_options = {
    "1": "Προσθήκη δημοσίευσης",
    "2": "Τροποποίηση δημοσίευσης",
    "3": "Διαγραφή δημοσίευσης",
    "4": "Προβολή δημοσίευσεων", 
    "5": "Προβολή συγγραφέων και ιδρυμάτων"
    #"6": "Διαγραφή χρήστη"

}

def sign_in():
    username = input("Εισάγετε το username σας: ").strip()
    password = input("Εισάγετε τον κωδικό πρόσβασης σας: ").strip()
    try:
        user = verify_user(username, password)
        if not user:
            show_error("Λάθος username ή κωδικός.")
            return None
        print("\nΕπιτυχής σύνδεση.\n")
        return user  # χρήσιμο να επιστρέφεις και τα στοιχεία
    except Exception as e:
        show_error(f"Σφάλμα σύνδεσης: {e}")
        return None


def sign_up():
    email = input("Εισάγετε το email σας: ").strip()
    fullname = input("Εισάγετε το ονοματεπώνυμο σας: ").strip()
    username = input("Εισάγετε username: ").strip()
    password = input("Εισάγετε κωδικό πρόσβασης: ").strip()
    user = {'username': username, 'password': password, 'email': email, 'fullname': fullname}
    try:
        new_user(user['username'], user['email'], user['fullname'], user['password'])
        print("\nΕπιτυχής εγγραφή.\n")
        return True
    except ValueError as e:
        show_error(str(e))
        return False

def show_general_subtree(username):
    try:
        general_id = get_or_create_folder("Γενικά", username)
        print_folder_subtree(username, general_id, show_pubs=True)
    except Exception as e:
        show_error(f"Σφάλμα κατά την εμφάνιση subtree: {e}")


def show_folder_contents_detailed(folder_id, username):
    subfolders = get_subfolders(folder_id, username)  # [(id_fakelou, Onoma), ...]
    pubs = get_folder_publications_details(folder_id, username)  # list[dict]

    print("\n📁 Υποφάκελοι:")
    if not subfolders:
        print("  (Κανένας υποφάκελος)")
    else:
        for fid, name in subfolders:
            print(f"  [{fid}] {name}")

    show_publications_list(pubs, title="📄 Δημοσιεύσεις στον φάκελο")

def show_folder_under_general(username):
    try:
        general_id = get_or_create_folder("Γενικά", username)

        print_folder_subtree(username, general_id, show_pubs=False)

        raw = input("\nΔώστε το ID του φακέλου που θέλετε να εμφανίσετε: ").strip()
        if not raw.isdigit():
            show_error("Μη έγκυρο ID.")
            return

        folder_id = int(raw)

        if not is_in_general_subtree(folder_id, general_id, username):
            show_error("Ο φάκελος δεν βρίσκεται μέσα στον 'Γενικά'.")
            return

        show_folder_contents_detailed(folder_id, username)

    except Exception as e:
        show_error(f"Σφάλμα στην επιλογή 'Εμφάνιση φακέλου': {e}")



def show_comments_for_pub(username): #προβολή σχολίων του χρήστη για μια δημοσίευση
    doi = input("Εισάγετε το DOI της δημοσίευσης για να δείτε τα σχόλιά σας: ").strip()
    if not doi:
        show_error("Το DOI δεν μπορεί να είναι κενό.")
        return

    try:
        comments = get_comments_by_pub_and_user(doi, username)

        if not comments:
            print(f"\nΔεν έχετε γράψει σχόλια στη δημοσίευση με DOI: {doi}")
            return

        print(f"\n--- ΤΑ ΣΧΟΛΙΑ ΣΑΣ ΓΙΑ ΤΗ ΔΗΜΟΣΙΕΥΣΗ {doi} ---")
        for c in comments:
            print(f"ID: {c['id_sxoliou']} | Ημερομηνία: {c['Imer_dimiourgias']}")
            print(f"Σχόλιο: {c['Periexomeno']}")
            print("-" * 40)

    except Exception as e:
        show_error(f"Σφάλμα κατά την ανάκτηση σχολίων: {e}")

def add_publication(username):
    doi = input("Εισάγετε το DOI της δημοσίευσης: ").strip()
    if not doi:
        show_error("Το DOI δεν μπορεί να είναι κενό.")
        return

    confirm = input("Θέλετε να ορίσετε συγκεκριμένο φάκελο; (ν/ο): ").strip().lower()

    try:
        # Εξασφαλίζουμε ότι υπάρχει ο root "Γενικά"
        general_id = get_or_create_folder("Γενικά", username)  # root (parent_id=None)

        if confirm == "ν":
            folder_name = input("Εισάγετε όνομα φακέλου: ").strip()
            if not folder_name:
                show_error("Το όνομα φακέλου δεν μπορεί να είναι κενό.")
                return

            # Δημιουργία/εύρεση φακέλου ΚΑΤΩ από το "Γενικά"
            folder_id = get_or_create_folder(folder_name, username, parent_id=general_id)
        else:
            # Default: "Γενικά"
            folder_id = general_id

        add_pub_to_folder(doi, folder_id, username)
        show_message("Επιτυχής εισαγωγή δημοσίευσης σε φάκελο.")

    except ValueError as e:
        show_error(str(e))
    except Exception as e:
        show_error(f"Σφάλμα κατά την προσθήκη δημοσίευσης: {e}")


def delete_publication_from_folder(username):
    try:
        doi = input("Εισάγετε το DOI της δημοσίευσης που θέλετε να αφαιρέσετε: ").strip()
        if not doi:
            show_error("Το DOI δεν μπορεί να είναι κενό.")
            return

        general_id = get_or_create_folder("Γενικά", username)

        # δείχνουμε subtree για να δει ids
        print_folder_subtree(username, general_id, show_pubs=False)

        raw = input("\nΔώστε το ID του φακέλου από τον οποίο θα αφαιρεθεί η δημοσίευση: ").strip()
        if not raw.isdigit():
            show_error("Μη έγκυρο ID.")
            return
        folder_id = int(raw)

        # επιτρέπουμε μόνο φακέλους μέσα στο Γενικά
        if not is_in_general_subtree(folder_id, general_id, username):
            show_error("Ο φάκελος δεν βρίσκεται μέσα στον 'Γενικά'.")
            return

        confirm = input(f"Θέλετε σίγουρα να αφαιρέσετε το DOI {doi} από τον φάκελο ID {folder_id}; (ν/ο): ").strip().lower()
        if confirm != "ν":
            show_message("Ακύρωση αφαίρεσης δημοσίευσης.")
            return

        remove_pub_from_folder(doi, folder_id, username)
        show_message("Η δημοσίευση αφαιρέθηκε επιτυχώς από τον φάκελο.")

    except LookupError as e:
        show_error(str(e))
    except Exception as e:
        show_error(f"Σφάλμα κατά την αφαίρεση δημοσίευσης: {e}")


def new_folder(username):
    folder_name = input("Εισάγετε το όνομα του φακέλου για δημιουργία: ").strip()
    if not folder_name:
        show_error("Το όνομα φακέλου δεν μπορεί να είναι κενό.")
        return

    # Ρωτάμε τον χρήστη αν θέλει συγκεκριμένο φάκελο parent
    confirm = input("Θέλετε να ορίσετε κύριο φάκελο; (ν/ο): ").strip().lower()

    try:
        if confirm == "ν":
            parent_name = input("Εισάγετε το όνομα του κύριου φακέλου: ").strip()
            if not parent_name:
                show_error("Το όνομα του κύριου φακέλου δεν μπορεί να είναι κενό.")
                return

            parent_id = get_or_create_folder(parent_name, username)

        else:
            parent_id = get_or_create_folder("Γενικά", username)

        folder_id = get_or_create_folder(folder_name, username, parent_id)
        print("Επιτυχής δημιουργία φακέλου.")

    except ValueError as e:
        show_error(str(e))

def delete_user_folder(username):
    try:
        general_id = get_or_create_folder("Γενικά", username)

        # δείχνουμε subtree για να δει ids
        print_folder_subtree(username, general_id, show_pubs=False)

        raw = input("\nΔώστε το ID του φακέλου που θέλετε να διαγράψετε: ").strip()
        if not raw.isdigit():
            show_error("Μη έγκυρο ID.")
            return
        folder_id = int(raw)

        # δεν επιτρέπουμε να σβήσει τον root Γενικά
        if folder_id == general_id:
            show_error("Δεν μπορείτε να διαγράψετε τον φάκελο 'Γενικά'.")
            return

        # επιτρέπουμε μόνο φακέλους μέσα στο Γενικά
        if not is_in_general_subtree(folder_id, general_id, username):
            show_error("Ο φάκελος δεν βρίσκεται μέσα στον 'Γενικά'.")
            return

        confirm = input(f"Θέλετε σίγουρα να διαγράψετε τον φάκελο με ID {folder_id}; (ν/ο): ").strip().lower()
        if confirm != "ν":
            show_message("Ακύρωση διαγραφής φακέλου.")
            return

        delete_folder(folder_id, username)
        show_message("Επιτυχής διαγραφή φακέλου.")

    except LookupError as e:
        show_error(str(e))
    except Exception as e:
        show_error(f"Σφάλμα κατά τη διαγραφή φακέλου: {e}")


def create_comment(username):
    doi = input("Εισάγετε το doi της δημοσίευσης: ").strip()
    comment = input("Γράψτε το σχόλιο: ").strip()

    try:
        insert_comment_to_pub(doi, username, comment)
        print("Επιτυχής εισαγωγή σχολίου.")
    except ValueError as e:
        print(e)
    except Exception as e:
        print("Παρουσιάστηκε απρόσμενο σφάλμα:", e)

def delete_user_comment(username):
    doi = input("Εισάγετε το DOI της δημοσίευσης στην οποία είναι το σχόλιο: ").strip()

    try:
        comments = get_comments_by_pub_and_user(doi, username)

        if not comments:
            print("Δεν έχετε γράψει σχόλια σε αυτή τη δημοσίευση.")
            return

        print("\nΤα σχόλιά σας:")
        for c in comments:
            print(f"[{c['id_sxoliou']}] {c['Periexomeno']}")

        try:
            comment_id = int(input("\nΔώστε το ID του σχολίου που θέλετε να διαγράψετε: "))
        except ValueError:
            show_error("Μη έγκυρο ID σχολίου.")
            return

        confirm = input(f"Θέλετε σίγουρα να διαγράψετε το σχόλιο με ID {comment_id}; (ν/ο): ").strip().lower()

        if confirm != "ν":
            print("Ακύρωση διαγραφής σχολίου.")
            return

        delete_comment(comment_id, username)
        print("Επιτυχής διαγραφή σχολίου.")

    except LookupError as e:
        show_error(str(e))

    except Exception as e:
        show_error(f"Σφάλμα κατά τη διαγραφή σχολίου: {e}")

def search_pub():
    search = input("Εισάγετε το DOI ή τον τίτλο της δημοσίευσης: ").strip()

    if not search:
        show_error("Η αναζήτηση δεν μπορεί να είναι κενή.")
        return

    try:
        results = search_publications(search)

        if not results:
            print("Δεν βρέθηκαν δημοσιεύσεις.")
            return

        print("\nΑποτελέσματα αναζήτησης:")
        for pub in results:
            print(f"- {pub['DOI']} | {pub['Titlos']}")

    except Exception as e:
        show_error(f"Σφάλμα κατά την αναζήτηση: {e}")

def search_pub_by_author():
    name = input("Εισάγετε ονοματεπώνυμο συγγραφέα: ").strip()
    if not name:
        show_error("Η αναζήτηση δεν μπορεί να είναι κενή.")
        return

    try:
        authors = search_authors(name)
        if not authors:
            print("Δεν βρέθηκαν συγγραφείς.")
            return

        print("\nΑποτελέσματα συγγραφέων:")
        for a in authors:
            print(f"- {a['id_syggrafea']} | {a['Onomateponymo']}")

        chosen = input("\nΕισάγετε το id του συγγραφέα από τη λίστα: ").strip()
        if not chosen:
            show_error("Πρέπει να επιλέξετε id συγγραφέα.")
            return
        if not chosen.isdigit():
            show_error("Το id πρέπει να είναι αριθμός.")
            return

        author_id = int(chosen)
        pubs = get_pubs_by_author(author_id)

        if not pubs:
            print("Δεν βρέθηκαν δημοσιεύσεις για τον επιλεγμένο συγγραφέα.")
            return

        print("\nΔημοσιεύσεις συγγραφέα:")
        for pub in pubs:
            print(f"- {pub['DOI']} | {pub['Titlos']}")

    except Exception as e:
        show_error(f"Σφάλμα κατά την αναζήτηση: {e}")

def search_pub_by_keyword():
    keyword = input("Εισάγετε λέξη-κλειδί: ").strip()
    if not keyword:
        show_error("Η αναζήτηση δεν μπορεί να είναι κενή.")
        return

    try:
        results = get_pubs_by_keyword(keyword)
        if not results:
            print("Δεν βρέθηκαν δημοσιεύσεις για τη συγκεκριμένη λέξη-κλειδί.")
            return

        print("\nΑποτελέσματα αναζήτησης:")
        for pub in results:
            print(f"- {pub['DOI']} | {pub['Titlos']}")

    except Exception as e:
        show_error(f"Σφάλμα κατά την αναζήτηση: {e}")

def admin_add_publication():
    doi = input("DOI: ").strip()
    title = input("Τίτλος: ").strip()
    language = input("Γλώσσα: ").strip()
    summary = input("Περίληψη (προαιρετικό): ").strip()
    url = input("URL (προαιρετικό): ").strip()

    if not doi or not title or not language:
        show_error("DOI, Τίτλος και Γλώσσα είναι υποχρεωτικά.")
        return

    pub_type = input("Τύπος δημοσίευσης (1=Περιοδικό, 2=Συνέδριο): ").strip()
    if pub_type == "1":
        pub_type = "Περιοδικό"
        extra_data = {
            "ISSN": input("ISSN: ").strip(),
            "Imer_dimosieysis": input("Ημερομηνία δημοσίευσης (YYYY-MM-DD): ").strip(),
            "Teyxos": input("Τεύχος: ").strip(),
            "Tomos": input("Τόμος: ").strip(),
            "Selides_periodikou": input("Σελίδες περιοδικού: ").strip(),
        }
        # βασικός έλεγχος
        if not extra_data["ISSN"] or not extra_data["Imer_dimosieysis"]:
            show_error("ISSN και Ημερομηνία δημοσίευσης είναι υποχρεωτικά για Περιοδικό.")
            return

    elif pub_type == "2":
        pub_type = "Συνέδριο"
        extra_data = {
            "ISBN": input("ISBN: ").strip(),
            "Onoma_synedriou": input("Όνομα συνεδρίου: ").strip(),
            "Imer_dieksagogis": input("Ημερομηνία διεξαγωγής (YYYY-MM-DD): ").strip(),
            "Topos_dieksagogis": input("Τόπος διεξαγωγής: ").strip(),
        }
        if not extra_data["ISBN"] or not extra_data["Onoma_synedriou"]:
            show_error("ISBN και Όνομα συνεδρίου είναι υποχρεωτικά για Συνέδριο.")
            return

    else:
        show_error("Μη έγκυρος τύπος. Δώστε 1 ή 2.")
        return

    try:
        insert_publication(
            doi=doi,
            title=title,
            language=language,
            summary=summary or None,
            url=url or None,
            pub_type=pub_type,
            extra_data=extra_data
        )
        show_message("Η δημοσίευση προστέθηκε επιτυχώς.")
    except ValueError as e:
        show_error(str(e))
    except Exception as e:
        show_error(f"Σφάλμα κατά την προσθήκη: {e}")


def admin_update_publication():
    doi = input("Εισάγετε DOI δημοσίευσης για τροποποίηση: ").strip()
    if not doi:
        show_error("Το DOI δεν μπορεί να είναι κενό.")
        return

    new_title = input("Εισάγετε νέο τίτλο: ").strip()
    if not new_title:
        show_error("Ο νέος τίτλος δεν μπορεί να είναι κενός.")
        return

    try:
        update_pub_title(doi, new_title)
        show_message("Ο τίτλος ενημερώθηκε επιτυχώς.")
    except LookupError as e:
        show_error(str(e))
    except Exception as e:
        show_error(f"Σφάλμα κατά την τροποποίηση: {e}")

def admin_delete_publication():
    doi = input("Εισάγετε DOI δημοσίευσης για διαγραφή: ").strip()
    if not doi:
        show_error("Το DOI δεν μπορεί να είναι κενό.")
        return

    confirm = input(f"Θέλετε σίγουρα να διαγράψετε τη δημοσίευση {doi}; (ν/ο): ").strip().lower()
    if confirm != "ν":
        show_message("Ακύρωση διαγραφής.")
        return

    try:
        delete_publication(doi)
        show_message("Η δημοσίευση διαγράφηκε επιτυχώς.")
    except LookupError as e:
        show_error(str(e))
    except RuntimeError as e:
        show_error(str(e))
    except Exception as e:
        show_error(f"Σφάλμα κατά τη διαγραφή: {e}")

def admin_view_publications():
    try:
        pubs = get_all_publications()
        show_publications_list(pubs, title="Όλες οι δημοσιεύσεις")
    except Exception as e:
        show_error(f"Σφάλμα κατά την προβολή: {e}")

def admin_view_authors_and_institutions():
    try:
        authors = get_all_authors()
        institutions = get_all_institutions()

        print("\n--- ΣΥΓΓΡΑΦΕΙΣ ---")
        if not authors:
            print("Δεν υπάρχουν συγγραφείς.")
        else:
            for a in authors:
                print(f"- {a['id_syggrafea']} | {a['Onomateponymo']}")

        print("\n--- ΙΔΡΥΜΑΤΑ ---")
        if not institutions:
            print("Δεν υπάρχουν ιδρύματα.")
        else:
            for i in institutions:
                print(f"- {i['id_idrymatos']} | {i['Onoma']} | {i['Dieythinsi']}")

    except Exception as e:
        show_error(f"Σφάλμα κατά την προβολή: {e}")



def handle_user_choice(choice, username):
    actions = {
        "1": lambda: show_general_subtree(username),
        "2": lambda: show_folder_under_general(username),
        "3": lambda: add_publication(username),
        "4": lambda: delete_publication_from_folder(username),
        "5": lambda: new_folder(username),
        "6": lambda: delete_user_folder(username),
        "7": lambda: create_comment(username),
        "8": lambda: delete_user_comment(username),
        "9": lambda: show_comments_for_pub(username),
        "10": lambda: search_pub(),
        "11": lambda: search_pub_by_author(),
        "12": lambda: search_pub_by_keyword(),
    }
    action = actions.get(choice)
    if not action:
        show_error("Μη έγκυρη επιλογή.")
        return
    action()



def handle_admin_choice(choice):
    actions = {
        "1": admin_add_publication,
        "2": admin_update_publication,
        "3": admin_delete_publication,
        "4": admin_view_publications,
        "5": admin_view_authors_and_institutions,
    }
    action = actions.get(choice)
    if not action:
        show_error("Μη έγκυρη επιλογή.")
        return
    action()


def app_loop():
    while True:
        show_menu(starting_options, title="ΑΡΧΙΚΟ ΜΕΝΟΥ")
        choice = input("Επιλογή: ").strip()

        if choice == "0":
            print("Έξοδος από την εφαρμογή.")
            break

        # 1) Σύνδεση
        if choice == "1":
            user = sign_in()
            if not user:
                continue

            username = user["Username"]  # προσοχή: έτσι το επιστρέφει η get_user_by_username
            admin = user.get("Is_admin") == 1

            if admin:
                admin_loop(username)
            else:
                user_loop(username)

        # 2) Εγγραφή
        elif choice == "2":
            sign_up()

        else:
            show_error("Μη έγκυρη επιλογή.")


def user_loop(username):
    while True:
        show_menu(user_options, title=f"ΜΕΝΟΥ ΧΡΗΣΤΗ ({username})")
        choice = input("Επιλογή: ").strip()
        if choice == "0":
            print("Αποσύνδεση.")
            break
        handle_user_choice(choice, username)


def admin_loop(username):
    while True:
        show_menu(admin_options, title=f"ΜΕΝΟΥ ADMIN ({username})")
        choice = input("Επιλογή: ").strip()
        if choice == "0":
            print("Αποσύνδεση.")
            break
        handle_admin_choice(choice)

if __name__ == "__main__":
    app_loop()

