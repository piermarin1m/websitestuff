import streamlit as st
import requests
from requests.exceptions import ConnectTimeout, RequestException

# Set page config FIRST with fixed Schoology title and icon
st.set_page_config(
    page_title="Schoology",
    page_icon="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRP_7kkj4YwJIWoBsxo6Dp2aXzqTNhRYYDrYA&s",
    layout="wide"
)

BACKEND_URL = "http://150.136.82.157:1692"
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
        # Check backend health first
        health_response = requests.get(f"{BACKEND_URL}/health", timeout=TIMEOUT_SECONDS)
        if health_response.status_code != 200:
            raise RequestException(f"Backend health check failed with status code: {health_response.status_code}")

        # Send request to `/fetch_website`
        fetch_response = requests.get(f"{BACKEND_URL}/fetch_website", params={"url": url}, timeout=TIMEOUT_SECONDS)
        if fetch_response.status_code == 200:
            # Embed fetched HTML using Streamlit components
            st.components.v1.html(fetch_response.text, height=800, scrolling=True)
        else:
            st.error(f"Failed to fetch website. Status code: {fetch_response.status_code}, Response: {fetch_response.text}")

    except ConnectTimeout:
        st.error("Connection to backend server timed out. Please verify the server is running and accessible.")
    except RequestException as e:
        st.error(f"Error connecting to backend: {str(e)}")
    except Exception as e:
        st.error(f"Unexpected error: {str(e)}")
