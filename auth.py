import streamlit as st
import random
import os

# ==========================================
# 0. ADMIN PASSWORD GATE
# ==========================================

ADMIN_PASSWORD = "admin"  # Change this to your desired password

def show_admin_password_gate():
    """Display admin password authentication screen before login page"""
    st.set_page_config(
        page_title="JSS SIDI PRO - Admin Access",
        layout="centered",
        initial_sidebar_state="collapsed"
    )
    
    st.title("🔒 JSS SIDI PRO")
    st.markdown("---")
    st.markdown("### Admin Access Required")
    st.write("Please enter the universal admin password to proceed.")
    
    # Admin password input
    admin_pass = st.text_input(
        "Admin Password",
        type="password",
        key="admin_password_field",
        placeholder="Enter admin password"
    )
    
    if st.button("Access System", use_container_width=True, type="primary"):
        if admin_pass == ADMIN_PASSWORD:
            st.session_state['admin_verified'] = True
            st.success("✅ Access Granted! Redirecting...")
            st.rerun()
        else:
            st.error("❌ Invalid admin password. Access denied.")

def is_admin_verified():
    """Check if admin password has been verified"""
    return st.session_state.get('admin_verified', False)

# ==========================================
# 1. AUTHENTICATION CORE LOGIC
# ==========================================

def update_password(user_id, new_password):
    """Overwrites the credentials.txt file in the user's folder"""
    try:
        user_folder = os.path.join("cloud_simulator", user_id)
        if not os.path.exists(user_folder):
            os.makedirs(user_folder)
            
        pw_path = os.path.join(user_folder, "credentials.txt")
        with open(pw_path, "w") as f:
            f.write(str(new_password))
        return True, "Password updated successfully!"
    except Exception as e:
        return False, f"Auth Error: {str(e)}"

def send_recovery_code(user_email):
    """Generates a 4-digit code and stores it in session state"""
    code = str(random.randint(1000, 9999))
    st.session_state['recovery_code'] = code
    return True, code

# ==========================================
# 2. UI COMPONENTS
# ==========================================

def show_auth_page():
    st.title("JSS SIDI PRO")
    st.subheader("Academic Assessment Management System")
    
    tab1, tab2 = st.tabs(["🔐Login", "Create Account"])

    with tab1:
        st.write("### User Login")
        
        email = st.text_input("Email Address", key="login_email_field", placeholder="teacher@example.com")
        password = st.text_input("Password", type="password", key="login_password_field")
        
        if st.button("Access System", key="login_submit_button", use_container_width=True):
            if email and password:
                # Logic to verify password would go here
                st.session_state['logged_in'] = True
                st.session_state['email'] = email
                st.session_state['user_id'] = email.replace(".", "_").replace("@", "_")
                st.rerun()
            else:
                st.error("Please enter both email and password.")

        # --- PASSWORD RECOVERY SECTION ---
        st.divider()
        with st.expander("Forgot Password?"):
            st.write("Enter your email to receive a 4-digit reset code.")
            recovery_email = st.text_input("Recovery Email", key="recovery_email_input")
            
            if st.button("Send Reset Code", use_container_width=True):
                if "@" in recovery_email:
                    success, code = send_recovery_code(recovery_email)
                    st.warning(f"📩 [SIMULATION] Your code is: **{code}**")
                    st.session_state['show_reset_field'] = True
                else:
                    st.error("Please enter a valid email.")

            if st.session_state.get('show_reset_field'):
                input_code = st.text_input("Enter 4-Digit Code", max_chars=4, key="recovery_code_verify")
                if st.button("Verify & Login", use_container_width=True):
                    if input_code == st.session_state.get('recovery_code'):
                        # Temporarily log them in and set code as password
                        u_id = recovery_email.replace(".", "_").replace("@", "_")
                        update_password(u_id, input_code)
                        
                        st.session_state['logged_in'] = True
                        st.session_state['email'] = recovery_email
                        st.session_state['user_id'] = u_id
                        st.success("Verified! Password reset to code. Please change it in Settings.")
                        st.rerun()
                    else:
                        st.error("Invalid code.")

    with tab2:
        st.write("### Register New School Account")
        new_email = st.text_input("Email Address", key="signup_email_field")
        new_pass = st.text_input("Create Password", type="password", key="signup_password_field")
        confirm_pass = st.text_input("Confirm Password", type="password", key="signup_confirm_field")
        
        if st.button("Register School", key="signup_submit_button", use_container_width=True):
            if new_email and new_pass == confirm_pass:
                user_id = new_email.replace(".", "_").replace("@", "_")
                update_password(user_id, new_pass) # Save initial password
                st.success("Account created! Switch to the Login tab.")
            else:
                st.error("Check your passwords.")

def is_user_logged_in():
    return st.session_state.get('logged_in', False)

def logout_user():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

def get_current_user():
    return {
        'email': st.session_state.get('email'),
        'user_id': st.session_state.get('user_id')
    }