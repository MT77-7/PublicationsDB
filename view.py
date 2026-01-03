from mymodel import (get_user_folders, get_folder_publications_details)

def show_message(message): #Εμφανίζει ένα μήνυμα επιτυχίας ή ενημέρωσης
    print(f"\n {message}")

def show_error(error_message): #Εμφανίζει ένα μήνυμα σφάλματος
    print(f"\n ΣΦΑΛΜΑ: {error_message}")

def show_menu(options, title="ΜΕΝΟΥ"): #εμφάνιση μενού
    print(f"\n=== {title} ===")
    for k, v in sorted(options.items(), key=lambda x: int(x[0])):
        print(f"{k}. {v}")
    print("0. Έξοδος")


def show_publications_list(publications, title="Δημοσιεύσεις"): #Εμφανίζει μια λίστα δημοσιεύσεων σε μορφή πίνακα
    if not publications:
        print(f"\n--- {title} ---")
        print("Δεν βρέθηκαν αποτελέσματα.")
        return

    print(f"\n--- {title} ---")
    print(f"{'DOI':<25} | {'Τίτλος':<50}")
    print("-" * 80)
    for pub in publications:
        #Κόβουμε τον τίτλο αν είναι πολύ μεγάλος
        display_title = (pub['Titlos'][:47] + '...') if len(pub['Titlos']) > 47 else pub['Titlos']
        print(f"{pub['DOI']:<25} | {display_title:<50}")

def show_publication_details(pub, authors=None, comments=None):  #Εμφανίζει όλες τις λεπτομέρειες μιας συγκεκριμένης δημοσίευσης
    print("\n" + "="*60)
    print(f"ΠΛΗΡΟΦΟΡΙΕΣ ΔΗΜΟΣΙΕΥΣΗΣ")
    print("="*60)
    print(f"Τίτλος:    {pub['Titlos']}")
    print(f"DOI:       {pub['DOI']}")
    print(f"Γλώσσα:    {pub['Glossa']}")
    print(f"Περίληψη:  {pub['Perilipsi'] if pub['Perilipsi'] else 'Δεν υπάρχει περίληψη.'}")
    print(f"URL:       {pub['URL']}")
    
    if authors:
        print(f"Συγγραφείς: {', '.join(authors)}")
    
    print("-" * 60)
    if comments:
        print("ΣΧΟΛΙΑ:")
        for c in comments:
            print(f"- [{c['Username']}]: {c['Keimeno_sxolioy']} ({c['Imeromhnia_sxolioy']})")
    else:
        print("Δεν υπάρχουν σχόλια για αυτή τη δημοσίευση.")
    print("="*60)

def print_folder_subtree(username, root_id, show_pubs=False): #εμφανίζει όλους τους φακέλους του χρήστη σε μορφή δέντρου
    folders = get_user_folders(username) 

    children_map = {} 
    name_map = {} 

    for f in folders:
        fid = f["id_fakelou"]
        parent_id = f["id_kyriou_fakelou"] 
        name = f["Onoma"]

        name_map[fid] = name
        children_map.setdefault(parent_id, []).append((fid, name))

    for pid in children_map:
        children_map[pid].sort(key=lambda x: x[1].lower())

    def _print(node_id, prefix="", is_last=True):
        name = name_map.get(node_id, "(Άγνωστος)")
        connector = "└─ " if is_last else "├─ "
        print(f"{prefix}{connector}📂 {name} [{node_id}]")

        if show_pubs:
            pubs = get_folder_publications_details(node_id, username)
            pub_prefix = prefix + ("   " if is_last else "│  ")
            for p in pubs:
                title = (p["Titlos"][:47] + "...") if len(p["Titlos"]) > 47 else p["Titlos"]
                print(f"{pub_prefix}   📄 {p['DOI']} | {title}")

        kids = children_map.get(node_id, [])
        new_prefix = prefix + ("   " if is_last else "│  ")
        for i, (child_id, _) in enumerate(kids):
            _print(child_id, new_prefix, is_last=(i == len(kids) - 1))

    root_name = name_map.get(root_id, "Γενικά")
    print(f"\n📁 {root_name} [{root_id}]")

    if show_pubs:
        root_pubs = get_folder_publications_details(root_id, username)
        for p in root_pubs:
            title = (p["Titlos"][:47] + "...") if len(p["Titlos"]) > 47 else p["Titlos"]
            print(f"   📄 {p['DOI']} | {title}")

    kids = children_map.get(root_id, [])
    if not kids:
        print("   (Κανένας υποφάκελος)")
        return

    for i, (child_id, _) in enumerate(kids):
        _print(child_id, prefix="", is_last=(i == len(kids) - 1))
