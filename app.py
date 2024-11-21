import streamlit as st
import requests
from requests.exceptions import ConnectTimeout, RequestException
import time
import urllib.parse

# Set page config with Schoology title and icon
st.set_page_config(
    page_title="Schoology",
    page_icon="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRP_7kkj4YwJIWoBsxo6Dp2aXzqTNhRYYDrYA&s",
    layout="wide"
)

# Backend configuration
BACKEND_URL = "http://150.136.82.157:1692"
TIMEOUT_SECONDS = 30

# Display the title
st.title("Schoology")

# URL input
url = st.text_input("Enter URL to visit:", value="https://www.google.com")
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
        except (ConnectTimeout, RequestException) as e:
            st.error(f"Error connecting to backend: {str(e)}")
        except Exception as e:
            st.error(f"Unexpected error: {str(e)}")

# Main content area
if st.button("Visit URL"):
    try:
        # Verify backend availability
        health_response = requests.get(f"{BACKEND_URL}/health", timeout=TIMEOUT_SECONDS)
        if health_response.status_code != 200:
            raise RequestException(f"Backend health check failed: {health_response.status_code}")
        
        # Proxied URL
        encoded_url = urllib.parse.quote(url, safe='')
        proxied_url = f"{BACKEND_URL}/fetch_website?url={encoded_url}"
        
        # Display the iframe
        st.markdown(
            f"""
            <div style="width: 100%; height: 800px; overflow: hidden; border: 1px solid #ddd; border-radius: 10px;">
                <iframe 
                    src="{proxied_url}"
                    width="100%" 
                    height="100%" 
                    style="width: 100%; height: 100%; border: none;"
                    sandbox="allow-same-origin allow-scripts allow-popups allow-forms"
                ></iframe>
            </div>
            """,
            unsafe_allow_html=True,
        )
    except ConnectTimeout:
        st.error("Connection to backend server timed out. Please verify the server is running and accessible.")
    except RequestException as e:
        st.error(f"Error connecting to backend: {str(e)}")
    except Exception as e:
        st.error(f"Unexpected error: {str(e)}")
