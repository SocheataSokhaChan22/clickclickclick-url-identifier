import streamlit as st
import time
import requests
from bs4 import BeautifulSoup
from PIL import Image, ImageDraw
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from os.path import exists
import machine_learning as ml
import feature_extraction as fe
from streamlit_extras.let_it_rain import rain 

# Set up Streamlit page configuration and custom CSS
st.set_page_config(
    page_title="ClickClickClick URL Identifier",
    page_icon="logo.png",
    layout="wide",
)

# Custom CSS for improved visibility and color display
st.markdown("""
    <style>
    .stApp {
        color: #333;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .stTitle {
        color: #333;
        font-size: 36px;
    }
    .stHeader {
        color: #333;
    }
    .stSubheader {
        color: #333;
    }
    .stTextInput > div > div > input {
        border: 2px solid #E97451;
    }
    .stSelectBox > div > div > {
        border: 2px solid #E97451;
    }
    .logo {
        display: block;
        margin: 20px auto;
        width: 80%;
        max-width: 500px;
    }
    </style>
    """, unsafe_allow_html=True)

# Add a logo/image
st.image("logo.png", output_format='PNG', width=500)
st.title('ClickClickClick URL Identifier')
st.write('ClickClickClick helps you detect malicious links in emails, text messages, and other online content.')
st.subheader('Disclaimer')
st.write('Our tools are intended to help users identify potential phishing links or legitimate URLs. While we strive for accuracy, results may vary. We are not liable for any damages resulting from tool use. By using our services, you agree to these terms.')

def get_driver(width, height):
    options = Options()
    options.add_argument('--disable-gpu')
    options.add_argument('--headless')
    options.add_argument(f"--window-size={width}x{height}")
    
    service = Service('/Users/socheatasokhachan/Desktop/testclicktestclick/chromedriver')  # Specify the path to your ChromeDriver
    driver = webdriver.Chrome(service=service, options=options)
    
    return driver

def get_screenshot(app_url, width, height):
    driver = get_driver(width, height)
    if app_url.endswith('streamlit.app'):
        driver.get(f"{app_url}/~/+/")
    else:
        driver.get(app_url)
            
    time.sleep(3)
            
    # Explicitly wait for an essential element to ensure content is loaded
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
            
    # Capture the screenshot
    driver.save_screenshot('screenshot.png')
    driver.quit()

def submit_url_to_urlscan(url, visibility='public'):
    headers = {'API-Key': 'd88e6346-ac33-4375-a6bb-1acbeca77aa1', 'Content-Type': 'application/json'}
    data = {"url": url, "visibility": visibility}
    response = requests.post('https://urlscan.io/api/v1/scan/', headers=headers, json=data)
    time.sleep(10)  # Initial wait before starting to poll
    max_attempts = 30  # Maximum number of attempts
    interval_seconds = 2  # Polling interval in seconds
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Failed to submit URL to urlscan.io. Status code: {response.status_code}")
        st.error(f"Response: {response.text}")
        return None

def example_safe():
    rain(
        emoji="💅",
        font_size=54,
        falling_speed=5,
        animation_length=5,
    )

def example_phishing():
    rain(
        emoji="💩",
        font_size=54,
        falling_speed=5,
        animation_length=5,
    )

width = 1920 
height = 1080

# Initialize session state
if 'submitted' not in st.session_state:
    st.session_state.submitted = False

# Input URL form
with st.form("my_form"):
    app_url = st.text_input('Input URL here').rstrip('/')
    visibility = st.selectbox("Select Scan Visibility", ["public", "unlisted", "private - Scan"])
    
    submitted = st.form_submit_button("Submit")
    if submitted:
        if app_url:
            get_screenshot(app_url, width, height)
            st.session_state.submitted = True
            
            # Phishing Detection
            try:
                response = requests.get(app_url, verify=False, timeout=4)
                if response.status_code != 200:
                    st.error("HTTP connection was not successful for the URL: {}".format(app_url))
                else:
                    soup = BeautifulSoup(response.content, "html.parser")
                    vector = [fe.create_vector(soup)]
                    result = ml.rf_model.predict(vector)
                    if result[0] == 0:
                        st.success("This website link is safe")
                        example_safe()
                    else:
                        st.warning("Attention! This website link is a potential PHISHING!")
                        example_phishing()
                    st.session_state.submitted = True

                    # Submit URL to urlscan.io
                    st.info('Submitting URL to urlscan.io...')
                    urlscan_response = submit_url_to_urlscan(app_url, visibility)
                    if urlscan_response:
                        scan_id = urlscan_response['uuid']
                        st.success(f':orange[Scan complete] By clicking the link here [URLScan website](https://urlscan.io/result/{scan_id}/) We directly connect you to view information such as screenshot of the URL, domains, IPs, Autonomous System (AS) numbers, hashes, etc. We integrate the APIs of urlscan.io to provide more detailed information about the URL infrastructure in summary results.')
            except requests.exceptions.RequestException as e:
                st.error("Error: {}".format(e))

# Display screenshot result if submitted
if st.session_state.submitted and exists('screenshot.png'):
    st.image('screenshot.png', caption="Live Screenshot of the URL", use_column_width=True)

    with open("screenshot.png", "rb") as file:
        btn = st.download_button(
            label="Download image",
            data=file,
            file_name="screenshot.png",
            mime="image/png"
        )

st.header("About ClickClickClick URL Identifier")
st.write('ClickClickClick URL Identifier is a tool developed by 3 junior students of the MIS department at Paragon International University.') 
st.write('Project Members:')
st.write('- Morita Chhea')
st.write('- Socheata Sokhachan')
st.write('- Sophy Do')        
st.write('ClickClickClick URL Identifier detects phishing and malicious websites using a machine-learning algorithm. The tool uses high-quality datasets containing phishing URLs and trains them into a model that can differentiate between legitimate and malicious ones.')
st.write('While "https://www.clickclickclick.tech/" is an online phishing awareness campaign that aims to educate people online on how to aware of phishing link, understanding how it works and how to protect themself.')
st.write('This online campaign runs by Rosa Rin, a senior student from Department of Media and Communication at RUPP and his team.')

st.subheader('About Data set')
st.write('We collect data set from:')
st.write('1. Phishtank.org as a data source for phishing URLs')
st.write('2. Tranco-list.eu as a data source for legitimate websites')
st.write('Total of 26,584 websites: **16,060 legitimate** websites | **10,524 phishing** websites')

st.subheader('Machine Learning Model Accuracy Result')
st.write('We used 4 different ML classifiers from scikit-learn and tested them using k-fold cross validation. We obtained their confusion matrices and calculated their accuracy, precision, and recall scores. The comparison table is below:')
st.table(ml.df_results)
st.write('NB = Gaussian Naive Bayes')
st.write('SVM = Support Vector Machine')
st.write('DT = Decision Tree')
st.write('RF = Random Forest')

st.write('As a result, the Random Forest model has the highest accuracy.')
st.write('ClickClickClick URL Identifier uses the Random Forest Model to detect phishing links.')