import streamlit as st
import pandas as pd
import json
import os
import re
import sys
from datetime import datetime

# --- CONFIG ---
DATA_FILE = "contacts_pro.json"

# --- UTILITY FUNCTIONS ---
def load_data():
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r") as f:
                return json.load(f)
    except Exception as e:
        print("Error loading data:", e)
    return []

def save_data(contacts):
    try:
        with open(DATA_FILE, "w") as f:
            json.dump(contacts, f, indent=4)
    except Exception as e:
        print("Error saving data:", e)

def validate_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

def validate_phone(phone):
    return phone.isdigit() and len(phone) >= 10

# --- CLI MODE ---
def cli_menu():
    contacts = load_data()

    while True:
        print("\n📇 CONTACT MANAGEMENT SYSTEM")
        print("1. Add Contact")
        print("2. View Contacts")
        print("3. Search Contact")
        print("4. Filter Contacts")
        print("5. Update Contact")
        print("6. Delete Contact")
        print("7. Exit")

        choice = input("Enter choice: ")

        if choice == "1":
            name = input("Name: ")
            phone = input("Phone: ")
            email = input("Email: ")
            city = input("City: ")
            company = input("Company: ")

            if not validate_email(email) or not validate_phone(phone):
                print("Invalid email or phone")
                continue

            new_id = max([c['id'] for c in contacts], default=0) + 1
            contacts.append({
                "id": new_id,
                "name": name,
                "phone": phone,
                "email": email,
                "city": city,
                "company": company
            })
            save_data(contacts)
            print("✅ Contact added")

        elif choice == "2":
            for c in contacts:
                print(c)

        elif choice == "3":
            q = input("Search: ").lower()
            for c in contacts:
                if q in c['name'].lower() or q in c['phone'] or q in c['email'].lower():
                    print(c)

        elif choice == "4":
            city = input("City filter: ")
            company = input("Company filter: ")
            for c in contacts:
                if (city.lower() in c['city'].lower() if city else True) and \
                   (company.lower() in c['company'].lower() if company else True):
                    print(c)

        elif choice == "5":
            cid = int(input("Enter ID to update: "))
            for c in contacts:
                if c['id'] == cid:
                    c['name'] = input(f"Name ({c['name']}): ") or c['name']
                    c['phone'] = input(f"Phone ({c['phone']}): ") or c['phone']
                    c['email'] = input(f"Email ({c['email']}): ") or c['email']
                    c['city'] = input(f"City ({c['city']}): ") or c['city']
                    c['company'] = input(f"Company ({c['company']}): ") or c['company']
                    save_data(contacts)
                    print("✅ Updated")
                    break

        elif choice == "6":
            val = input("Enter ID or Name to delete: ")
            contacts = [c for c in contacts if str(c['id']) != val and c['name'].lower() != val.lower()]
            save_data(contacts)
            print("🗑 Deleted")

        elif choice == "7":
            break

# --- CLI SWITCH ---
if len(sys.argv) > 1 and sys.argv[1] == "cli":
    cli_menu()
    exit()

# --- STREAMLIT UI ---
st.set_page_config(page_title="Apex CRM Pro", page_icon="📇", layout="wide")

contacts = load_data()

# --- SIDEBAR ---
st.sidebar.title("💎 Apex CRM")
menu = ["📊 Overview", "👤 Add Contact", "🔎 Search & Filters", "✏️ Update Contact", "🗑 Delete Contact", "📁 Export/Import"]
choice = st.sidebar.radio("Menu", menu)

# --- OVERVIEW ---
if choice == "📊 Overview":
    st.title("Dashboard")

    if contacts:
        df = pd.DataFrame(contacts)

        sort_choice = st.selectbox("Sort By:", ["Newest First", "Name", "Company"])
        if sort_choice == "Name":
            df = df.sort_values("name")
        elif sort_choice == "Company":
            df = df.sort_values("company")
        else:
            df = df.sort_values("id", ascending=False)

        st.dataframe(df)
    else:
        st.info("No contacts available")

# --- ADD ---
elif choice == "👤 Add Contact":
    st.title("Add Contact")

    name = st.text_input("Name")
    phone = st.text_input("Phone")
    email = st.text_input("Email")
    city = st.text_input("City")
    company = st.text_input("Company")

    if st.button("Add"):
        if not name or not phone or not email:
            st.error("Fill required fields")
        elif not validate_email(email):
            st.error("Invalid email")
        elif not validate_phone(phone):
            st.error("Invalid phone")
        else:
            new_id = max([c['id'] for c in contacts], default=0) + 1
            contacts.append({
                "id": new_id,
                "name": name,
                "phone": phone,
                "email": email,
                "city": city,
                "company": company,
                "date_added": datetime.now().strftime("%Y-%m-%d")
            })
            save_data(contacts)
            st.success("Added successfully")

# --- SEARCH ---
elif choice == "🔎 Search & Filters":
    st.title("Search & Filter")

    query = st.text_input("Search").lower()

    city_list = ["All"] + list(set([c['city'] for c in contacts if c['city']]))
    company_list = ["All"] + list(set([c['company'] for c in contacts if c['company']]))

    selected_city = st.selectbox("City", city_list)
    selected_company = st.selectbox("Company", company_list)

    results = [c for c in contacts if query in c['name'].lower() or query in c['phone'] or query in c['email'].lower()]

    if selected_city != "All":
        results = [c for c in results if c['city'] == selected_city]

    if selected_company != "All":
        results = [c for c in results if c['company'] == selected_company]

    st.write(results)

# --- UPDATE ---
elif choice == "✏️ Update Contact":
    st.title("Update Contact")

    ids = [c['id'] for c in contacts]
    selected_id = st.selectbox("Select ID", ids)

    contact = next((c for c in contacts if c['id'] == selected_id), None)

    if contact:
        name = st.text_input("Name", contact['name'])
        phone = st.text_input("Phone", contact['phone'])
        email = st.text_input("Email", contact['email'])
        city = st.text_input("City", contact['city'])
        company = st.text_input("Company", contact['company'])

        if st.button("Update"):
            contact.update({
                "name": name,
                "phone": phone,
                "email": email,
                "city": city,
                "company": company
            })
            save_data(contacts)
            st.success("Updated")

# --- DELETE ---
elif choice == "🗑 Delete Contact":
    st.title("Delete Contact")

    val = st.text_input("Enter ID or Name")

    if st.button("Delete"):
        new_contacts = [c for c in contacts if str(c['id']) != val and c['name'].lower() != val.lower()]
        save_data(new_contacts)
        st.success("Deleted")

# --- EXPORT/IMPORT ---
elif choice == "📁 Export/Import":
    st.title("Export / Import")

    if contacts:
        df = pd.DataFrame(contacts)
        csv = df.to_csv(index=False).encode()
        st.download_button("Download CSV", csv, "contacts.csv")

    file = st.file_uploader("Upload CSV", type="csv")
    if file:
        df_new = pd.read_csv(file)
        new_data = df_new.to_dict("records")

        current_max = max([c['id'] for c in contacts], default=0)
        for i, item in enumerate(new_data):
            item['id'] = current_max + i + 1

        contacts.extend(new_data)
        save_data(contacts)
        st.success("Imported")
        