import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import os 
from kaggle.api.kaggle_api_extended import KaggleApi
import io 
import zipfile


st.set_page_config(page_title="DATALAB", page_icon="📊", layout="centered")

# Function to handle CSV download
def download_csv(df):
    csv = df.to_csv(index=False)
    return csv.encode('utf-8')

# Main title
st.title("Bienvenue sur DATALAB")
st.markdown("## Choisissez une option pour commencer :")

# Button container
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("Importer un dataset", key="import"):
        st.session_state["page"] = "import"

with col2:
    if st.button("Créer un dataset", key="create"):
        st.session_state["page"] = "create"

with col3:
    if st.button("Rechercher un dataset", key="search"):
        st.session_state["page"] = "search"

# Handle button navigation
if "page" in st.session_state:
    if st.session_state["page"] == "import":
        st.write("### Importer un dataset")
        uploaded_file = st.file_uploader("Upload your dataset (CSV or Excel):")
        
        if uploaded_file:
            # Load the dataset into a DataFrame
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            elif uploaded_file.name.endswith('.xlsx'):
                df = pd.read_excel(uploaded_file)
            else:
                st.error("Please upload a CSV or Excel file.")
                df = None

            # Show the uploaded dataset
            if df is not None:
                st.success("Dataset uploaded successfully!")
                st.dataframe(df)  # Display the dataset as a table

    elif st.session_state.get("page") == "create":
        st.write("### Créer un dataset")
        
        # Step 1: Input the number of rows and columns to create
        num_columns = st.number_input("Enter the number of columns:", min_value=1, value=2)
        num_rows = st.number_input("Enter the number of rows:", min_value=1, value=1)
        
        # Initialize list to store column names
        columns = []
        
        # Step 2: Allow the user to enter column names based on the number of columns selected
        st.write("#### Enter column names:")
        for i in range(num_columns):
            column_name = st.text_input(f"Column {i + 1} name:", key=f"col_{i}")
            if column_name:
                columns.append(column_name)
        
        # Step 3: Create a table with input fields for each row and column
        st.write("#### Enter values for each row:")
        data = []
        for i in range(num_rows):
            row_data = []
            for col in columns:
                value = st.text_input(f"Value for '{col}' (Row {i + 1}):", key=f"value_{col}_{i}")
                row_data.append(value)
            data.append(row_data)

        # Step 4: Display the table and handle downloads when the user clicks the "Create Dataset" button
        if st.button("Create Dataset"):
            if columns and data:
                df_created = pd.DataFrame(data, columns=columns)
                st.success("Dataset created successfully!")
                st.dataframe(df_created)  # Display the created dataset
                
                # Buttons to download CSV or Excel
                st.write("#### Download the dataset")
                
                # Download CSV
                csv = download_csv(df_created)
                st.download_button(
                    label="Download as CSV",
                    data=csv,
                    file_name="dataset.csv",
                    mime="text/csv"
                )
                
            else:
                st.error("Please fill in all the necessary fields.")

    elif st.session_state["page"] == "search":
        st.write("### Rechercher un dataset")

        search_query = st.text_input("Enter dataset name to search on Kaggle:")

        if search_query:
            # Set the path to your kaggle.json file
            os.environ['KAGGLE_CONFIG_DIR'] = r'C:\Users\Lenovo\.kaggle'

            # Initialize the Kaggle API
            api = KaggleApi()
            api.authenticate()

            # Search for datasets on Kaggle using the entered search query
            try:
                # Fetch the dataset list using the Kaggle API
                datasets = api.dataset_list(search=search_query)
                if datasets:
                    st.write(f"Found {len(datasets)} datasets on Kaggle:")
                    # Display the dataset names and allow users to click for details
                    for dataset in datasets:
                        dataset_name = dataset.ref
                        dataset_title = dataset.title
                        st.write(f"- {dataset_title}: [View Dataset on Kaggle](https://www.kaggle.com/datasets/{dataset_name})")

                        # Provide an option to download the dataset with a unique key
                        if st.button(f"Download {dataset_title}", key=f"download_{dataset_name}"):  # Unique key using dataset name
                            # Download the dataset directly from Kaggle
                            st.write(f"Downloading {dataset_title}...")
                            download_path = r'C:\Users\Lenovo\Documents\AISD\S1\Python\Projet'  # Correct path to store datasets
                            api.dataset_download_files(dataset_name, path=download_path, unzip=True)
                            st.success(f"Dataset {dataset_title} downloaded successfully!")

                            # Get the list of downloaded files
                            downloaded_files = os.listdir(download_path)
                            dataset_files = []

                            # Collect all relevant files (csv, excel, json, etc.)
                            for file in downloaded_files:
                                if file.endswith(('.csv', '.xlsx', '.json')):  # Handle different file types
                                    dataset_files.append(file)

                            if dataset_files:
                                # Display the most recently downloaded dataset
                                latest_file = max(dataset_files, key=lambda f: os.path.getmtime(os.path.join(download_path, f)))
                                st.write(f"Displaying dataset: {latest_file}")

                                # Ensure the full path of the downloaded file
                                dataset_file_path = os.path.join(download_path, latest_file)

                                # Display the dataset
                                try:
                                    if latest_file.endswith('.csv'):
                                        df = pd.read_csv(dataset_file_path, encoding='utf-8')  # Handle CSV
                                    elif latest_file.endswith('.xlsx'):
                                        df = pd.read_excel(dataset_file_path)  # Handle Excel
                                    elif latest_file.endswith('.json'):
                                        df = pd.read_json(dataset_file_path)  # Handle JSON
                                    else:
                                        st.warning(f"Unsupported file type: {latest_file}")

                                    # Show the dataframe
                                    if df.empty:
                                        st.warning(f"The file {latest_file} is empty.")
                                    else:
                                        st.dataframe(df)
                                except Exception as e:
                                    st.error(f"Error loading the file {latest_file}: {e}")
                            else:
                                st.warning("No suitable data files found in the downloaded dataset.")
                else:
                    st.warning("No datasets found for this search query.")
            except Exception as e:
                st.error(f"An error occurred: {e}")





