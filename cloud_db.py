import streamlit as st
import pandas as pd
import os

# ==========================================
# 1. DATABASE CONNECTION
# ==========================================

def get_firebase_db():
    """Returns the base directory for data storage"""
    base_dir = "cloud_simulator"
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
    return base_dir

# ==========================================
# 2. USER ISOLATION & STORAGE LOGIC
# ==========================================

def init_user_database(user_id):
    """Creates a private folder for a new user"""
    db_path = get_firebase_db()
    user_folder = os.path.join(db_path, user_id)
    if not os.path.exists(user_folder):
        os.makedirs(user_folder)
    return user_folder

def save_to_cloud_db(df, grade, user_id):
    """Saves data into the user's private folder"""
    try:
        user_folder = init_user_database(user_id)
        file_path = os.path.join(user_folder, f"{grade}_data.csv")
        
        if os.path.exists(file_path):
            existing_df = pd.read_csv(file_path)
            # Merge and remove duplicates based on Assessment Number
            df = pd.concat([existing_df, df]).drop_duplicates(subset=['assmt_no'], keep='last')
            
        df.to_csv(file_path, index=False)
        return True, f"Successfully saved to {grade} database!"
    except Exception as e:
        return False, f"Error saving data: {str(e)}"

def get_learners(user_id, grade):
    """Retrieves learners from the CSV and reconstructs the dictionary format"""
    db_path = get_firebase_db()
    file_path = os.path.join(db_path, user_id, f"{grade}_data.csv")
    
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        learners = []
        for _, row in df.iterrows():
            # Separate marks from the metadata columns
            metadata_cols = ['name', 'assmt_no', 'grade', 'Learner\'s Name', 'Assessment Number']
            marks = {col: row[col] for col in df.columns if col not in metadata_cols}
            
            learners.append({
                'name': row.get('name') or row.get('Learner\'s Name'),
                'assmt_no': row.get('assmt_no') or row.get('Assessment Number'),
                'grade': row.get('grade'),
                'marks': marks
            })
        return learners
    return []

# ==========================================
# 3. SETTINGS & GRADES
# ==========================================

def get_user_settings(user_id):
    """Loads school branding settings"""
    return st.session_state.get('user_settings', {
        'school_name': 'AL HASSAN JUNIOUR SCHOOL',
        'term_info': 'Term 1, 2026'
    })

def update_user_settings(user_id, settings):
    """Saves school branding"""
    st.session_state['user_settings'] = settings
    return True, "Settings synced to cloud"

def get_grades(user_id):
    """List of available grades"""
    return ["Grade 6", "Grade 7", "Grade 8", "Grade 9"]

# ==========================================
# 4. DATA MODIFICATION (FIXED & COMPLETED)
# ==========================================

def delete_learner(user_id, learner_id, grade):
    """PERMANENTLY erases a learner from the CSV file"""
    try:
        db_path = get_firebase_db()
        file_path = os.path.join(db_path, user_id, f"{grade}_data.csv")
        
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            
            # Identify columns to check
            id_col = 'assmt_no' if 'assmt_no' in df.columns else 'Assessment Number'
            
            # Filter the dataframe to EXCLUDE the learner
            initial_len = len(df)
            df = df[df[id_col].astype(str) != str(learner_id)]
            
            if len(df) < initial_len:
                df.to_csv(file_path, index=False)
                return True, f"Learner {learner_id} has been erased."
            else:
                return False, "Learner ID not found in the file."
        return False, "Database file does not exist."
    except Exception as e:
        return False, f"System Error: {str(e)}"

def update_learner_marks(user_id, learner_id, grade, new_marks_dict):
    """Updates specific marks for a learner in the CSV"""
    try:
        db_path = get_firebase_db()
        file_path = os.path.join(db_path, user_id, f"{grade}_data.csv")
        
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            id_col = 'assmt_no' if 'assmt_no' in df.columns else 'Assessment Number'
            
            # Find the row and update the columns
            mask = df[id_col].astype(str) == str(learner_id)
            for subject, score in new_marks_dict.items():
                if subject in df.columns:
                    df.loc[mask, subject] = score
            
            df.to_csv(file_path, index=False)
            return True, "Marks updated successfully."
        return False, "File not found."
    except Exception as e:
        return False, str(e)

def export_grade_data(user_id, grade):
    """Returns the raw dataframe for CSV downloading"""
    db_path = get_firebase_db()
    file_path = os.path.join(db_path, user_id, f"{grade}_data.csv")
    
    if os.path.exists(file_path):
        return pd.read_csv(file_path)
    return pd.DataFrame()