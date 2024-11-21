import streamlit as st
import requests
from requests.exceptions import ConnectTimeout, RequestException
import time
import urllib.parse

# Set page config FIRST with fixed Schoology title and icon
st.set_page_config(
    page_title="Schoology",
    page_icon="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRP_7kkj4YwJIWoBsxo6Dp2aXzqTNhRYYDrYA&s",
    layout="wide"
)

BACKEND_URL = "https://git.heroku.com/hidden-castle-92662.git"
TIMEOUT_SECONDS = 30

# Display the Schoology title
st.title("Schoology")

# Input for the URL to visit
url = st.text_input("Enter URL to visit:", value="https://www.google.com")

# Ensure URL has protocol
if url and not url.startswith(('http://', 'https://')):
    url = 'https://' + url

# Sidebar controls
with st.sidebar:
    st.header("Control Panel")
    
    # Action Controls Section
    st.subheader("Action Controls")
    action = st.selectbox("Select Action", ["Input Text"])
    target_selector = st.text_input("CSS Selector of Target Element:")
    value = st.text_input("Value (for input actions):")

    if st.button("Send Action"):
        try:
            with st.spinner("Executing action..."):
                response = requests.post(
                    f"{BACKEND_URL}/send_action", 
                    json={
                        "action": action.lower(),
                        "target": target_selector,
                        "value": value
                    },
                    timeout=TIMEOUT_SECONDS
                )
                if response.status_code == 200:
                    st.success("Action executed successfully")
                else:
                    st.error(f"Failed to execute action: {response.text}")
        except ConnectTimeout:
            st.error("Connection to backend server timed out. Please verify the server is running and accessible.")
        except RequestException as e:
            st.error(f"Error connecting to backend: {str(e)}")
        except Exception as e:
            st.error(f"Unexpected error: {str(e)}")

# Main content area - Visit URL button and iframe
if st.button("Visit URL"):
    try:
        print("\n" + "="*50)
        print(f"Frontend: Requesting URL: {url}")
        print("="*50 + "\n")
        
        encoded_url = urllib.parse.quote(url, safe='')
        proxied_url = f"{BACKEND_URL}/fetch_website?url={encoded_url}"
        print(f"Frontend: Sending request to backend: {proxied_url}")
        
        # First verify the backend is accessible
        requests.get(f"{BACKEND_URL}/health", timeout=TIMEOUT_SECONDS)
        
        # Add timestamp to prevent caching
        timestamp = int(time.time())
        
        # Create a container for the iframe with custom styling
        st.markdown(
            f"""
            <div style="width: 100%; height: 800px; overflow: hidden; border: 1px solid #ccc; border-radius: 5px;">
                <iframe 
                    src="{proxied_url}&t={timestamp}" 
                    width="100%" 
                    height="100%" 
                    frameborder="0" 
                    style="width: 100%; height: 100%; border: none; overflow: auto;"
                    sandbox="allow-same-origin allow-scripts allow-popups allow-forms allow-presentation"
                    allow="clipboard-read; clipboard-write; fullscreen"
                    referrerpolicy="no-referrer"
                ></iframe>
            </div>
            """,
            unsafe_allow_html=True,
        )
        print("Frontend: iframe created successfully\n")
    except ConnectTimeout:
        error_msg = "Connection to backend server timed out. Please verify the server is running and accessible."
        print(f"\nERROR: {error_msg}\n")
        st.error(error_msg)
    except RequestException as e:
        error_msg = f"Error connecting to backend: {str(e)}"
        print(f"\nERROR: {error_msg}\n")
        st.error(error_msg)
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        print(f"\nERROR: {error_msg}\n")
        st.error(error_msg)
