def show_message(message):
    """Εμφανίζει ένα απλό μήνυμα επιτυχίας ή ενημέρωσης."""
    print(f"\n✅ {message}")

def show_error(error_message):
    """Εμφανίζει ένα μήνυμα σφάλματος με ευδιάκριτο τρόπο."""
    print(f"\n❌ ΣΦΑΛΜΑ: {error_message}")

def show_menu(options, title="ΜΕΝΟΥ"):
    print(f"\n=== {title} ===")
    for k, v in sorted(options.items(), key=lambda x: int(x[0])):
        print(f"{k}. {v}")
    print("0. Έξοδος")


def show_publications_list(publications, title="Δημοσιεύσεις"):
    """Εμφανίζει μια λίστα δημοσιεύσεων σε μορφή πίνακα."""
    if not publications:
        print(f"\n--- {title} ---")
        print("Δεν βρέθηκαν αποτελέσματα.")
        return

    print(f"\n--- {title} ---")
    print(f"{'DOI':<25} | {'Τίτλος':<50}")
    print("-" * 80)
    for pub in publications:
        # Κόβουμε τον τίτλο αν είναι πολύ μεγάλος για να μην χαλάει ο πίνακας
        display_title = (pub['Titlos'][:47] + '...') if len(pub['Titlos']) > 47 else pub['Titlos']
        print(f"{pub['DOI']:<25} | {display_title:<50}")

def show_publication_details(pub, authors=None, comments=None):
    """Εμφανίζει όλες τις λεπτομέρειες μιας συγκεκριμένης δημοσίευσης."""
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

def show_folders(folders):
    """Εμφανίζει τους φακέλους του χρήστη."""
    if not folders:
        print("\n📂 Δεν έχετε δημιουργήσει φακέλους ακόμα.")
        return

    print("\n--- ΟΙ ΦΑΚΕΛΟΙ ΣΑΣ ---")
    for f in folders:
        parent = f" (Υποφάκελος του ID: {f['id_kyriou_fakelou']})" if f['id_kyriou_fakelou'] else ""
        print(f"ID: {f['id_fakelou']} | Όνομα: {f['Onoma']}{parent}")
