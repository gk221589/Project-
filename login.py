from auth import login_page, register_page, logout



# Handle Authentication
query_params = st.experimental_get_query_params()
current_page = query_params.get("page", ["login"])[0]
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
if not st.session_state.logged_in:
    if current_page == "register":
        register_page()
    else:
        login_page()
    st.stop()

# Logout button
st.sidebar.button("Logout", on_click=logout)

# Set background image function
def set_background(image_url):
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("{image_url}");
            background-size: cover;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# Set background for the main page
set_background("https://img.freepik.com/free-photo/veggie-quinoa-bowl-cooking-recipe_53876-110662.jpg?semt=ais_hybrid")