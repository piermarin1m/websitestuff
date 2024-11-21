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
        print("\n" + "="*50)
        print(f"Frontend: Requesting URL: {url}")
        print("="*50 + "\n")
        
        # First verify the backend is accessible
        try:
            # Health check
            health_response = requests.get(f"{BACKEND_URL}/health", timeout=TIMEOUT_SECONDS)
            if health_response.status_code != 200:
                raise RequestException(f"Backend health check failed with status code: {health_response.status_code}")
            
            # Make the fetch_website request
            encoded_url = urllib.parse.quote(url, safe='')
            proxied_url = f"{BACKEND_URL}/fetch_website?url={encoded_url}"
            print(f"Frontend: Fetching website content from: {proxied_url}")
            
            # Make the actual request to fetch_website
            fetch_response = requests.get(proxied_url, timeout=TIMEOUT_SECONDS)
            if fetch_response.status_code != 200:
                raise RequestException(f"Failed to fetch website: {fetch_response.text}")
            
            # Create a container for the website viewer
            viewer_container = st.container()
            with viewer_container:
                # Create a unique key for the iframe
                iframe_key = f"iframe_{int(time.time())}"
                
                # Custom HTML/CSS for a better website viewer
                st.markdown(
                    f"""
                    <style>
                        .website-viewer {{
                            width: 100%;
                            height: 800px;
                            border: 1px solid #ddd;
                            border-radius: 10px;
                            overflow: hidden;
                            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                            background: white;
                            position: relative;
                        }}
                        
                        .viewer-header {{
                            height: 40px;
                            background: #f5f5f5;
                            border-bottom: 1px solid #ddd;
                            display: flex;
                            align-items: center;
                            padding: 0 10px;
                        }}
                        
                        .viewer-address {{
                            flex-grow: 1;
                            background: white;
                            border: 1px solid #ddd;
                            border-radius: 15px;
                            padding: 5px 10px;
                            margin: 0 10px;
                            font-size: 14px;
                            color: #333;
                            overflow: hidden;
                            text-overflow: ellipsis;
                            white-space: nowrap;
                        }}
                        
                        .viewer-content {{
                            height: calc(100% - 40px);
                            overflow: hidden;
                        }}
                        
                        .website-iframe {{
                            width: 100%;
                            height: 100%;
                            border: none;
                        }}
                    </style>
                    
                    <div class="website-viewer">
                        <div class="viewer-header">
                            <div class="viewer-address">{url}</div>
                        </div>
                        <div class="viewer-content">
                            <iframe 
                                key="{iframe_key}"
                                class="website-iframe"
                                srcdoc='{fetch_response.text}'
                                sandbox="allow-same-origin allow-scripts allow-popups allow-forms 
                                         allow-modals allow-downloads allow-presentation allow-top-navigation 
                                         allow-popups-to-escape-sandbox"
                                allow="accelerometer; autoplay; clipboard-read; clipboard-write; 
                                       encrypted-media; fullscreen; geolocation; gyroscope; 
                                       microphone; midi; payment; picture-in-picture; 
                                       screen-wake-lock; web-share"
                            ></iframe>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            
            print("Frontend: Website viewer created successfully\n")
            
        except ConnectTimeout:
            raise RequestException("Backend server connection timed out. Please verify the server is running.")
        except ConnectionRefusedError:
            raise RequestException("Could not connect to backend server. Please verify the server is running on the correct port.")
        except RequestException as e:
            if "Connection refused" in str(e):
                raise RequestException("Backend server is not running. Please start the backend server first.")
            raise
            
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
