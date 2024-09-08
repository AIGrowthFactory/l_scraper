import streamlit as st
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import requests
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from textwrap import wrap

# Airtable bilgileri hesaba göre düzenlenecek.
# BASE_ID için> Help> API Documentation
# Token için> Builder Hub>Personel Access Token>Create New Token>All Scopes seçildi>Table'ın ait olduğu Base seçildi.
AIRTABLE_BASE_ID = 'YOUR_AIRTABLE_BASE_ID'
AIRTABLE_YOUR_SECRET_API_TOKEN = 'YOUR_AIRTABLE_SECRET_API_TOKEN'
AIRTABLE_TABLE_NAME = 'py-to-airtable'

endpoint = f'https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_NAME}'

def login_to_linkedin(driver, username, password):
    driver.get('https://www.linkedin.com/login')
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, 'username')))
    username_input = driver.find_element(By.ID, 'username')
    password_input = driver.find_element(By.ID, 'password')
    username_input.send_keys(username)
    password_input.send_keys(password)
    password_input.send_keys(Keys.RETURN)
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, 'global-nav__me')))

def get_company_info(driver, company_name, company_url):
    driver.get(company_url)
    WebDriverWait(driver, 20).until(lambda d: d.execute_script('return document.readyState') == 'complete')
    time.sleep(2)  # Sayfanın tamamen yüklenmesi için ek süre

    company_info = {
        "Name": company_name,
        "URL": company_url,
        "Description": "N/A",
        "Website": "N/A",
        "Area": "N/A",
        "Founded": "N/A",
        "Headquarters": "N/A"
    }

    try:
        description = driver.find_element(By.CSS_SELECTOR, 'section.artdeco-card p.break-words').text
        company_info["Description"] = description
    except Exception as e:
        st.write(f"Açıklama bulunamadı: {e}")

    try:
        website = driver.find_element(By.CSS_SELECTOR, 'dd a.link-without-visited-state').get_attribute('href')
        company_info["Website"] = website
    except Exception as e:
        st.write(f"Web sitesi bulunamadı: {e}")

    try:
        area = driver.find_element(By.CSS_SELECTOR, 'div.org-top-card-summary-info-list__info-item').text.split(",")[0]
        company_info["Area"] = area
    except Exception as e:
        st.write(f"Alan bulunamadı: {e}")

    try:
        # Metni bul
        founded_text = driver.find_element(By.CSS_SELECTOR, 'dl.overflow-hidden').text

        # 'Founded' veya 'Kuruluş Yılı' anahtar kelimesini bul ve sonrasındaki yılı çıkar
        if "Founded" in founded_text:
            start_index = founded_text.index("Founded") + len("Founded ")
            founded_year = founded_text[start_index:start_index + 4]
            company_info["Founded"] = founded_year
        elif "Kuruluş" in founded_text:
            start_index = founded_text.index("Kuruluş") + len("Kuruluş ")
            founded_year = founded_text[start_index:start_index + 4]
            company_info["Founded"] = founded_year
        else:
            company_info["Founded"] = "Founded veya Kuruluş Yılı bilgisi bulunamadı"
    except Exception as e:
        st.write(f"Kuruluş yılı bulunamadı: {e}")

    try:
        # Metni bul
        headquarters_text = driver.find_element(By.CSS_SELECTOR, 'dl.overflow-hidden').text

        # 'Headquarters' veya 'Genel Merkez' anahtar kelimesini bul ve sonrasındaki şehri çıkar
        if "Headquarters" in headquarters_text:
            start_index = headquarters_text.index("Headquarters") + len("Headquarters ")
            # Headquarters bilgisinin bulunduğu satırı ayır
            headquarters_city = headquarters_text[start_index:].split('\n')[0]
            company_info["Headquarters"] = headquarters_city
        elif "Genel Merkez" in headquarters_text:
            start_index = headquarters_text.index("Genel Merkez") + len("Genel Merkez ")
            # Genel Merkez bilgisinin bulunduğu satırı ayır
            headquarters_city = headquarters_text[start_index:].split('\n')[0]
            company_info["Headquarters"] = headquarters_city
        else:
            company_info["Headquarters"] = "Headquarters veya Genel Merkez bilgisi bulunamadı"
    except Exception as e:
        st.write(f"Merkez şehir bilgisi bulunamadı: {e}")

    return company_info


# Fields kısmı, Table başlıklarına özel olarak düzenlenecek.
def add_to_airtable(company_info):
    if company_info.get("Name") is None:
        return
    headers = {
        "Authorization": f"Bearer {AIRTABLE_YOUR_SECRET_API_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "records": [
            {
                "fields": {
                    "Şirket İsmi": company_info["Name"],
                    "Web Sitesi": company_info["Website"],
                    "Area": company_info["Area"],
                    "Kuruluş Yılı": company_info["Founded"],
                    "Merkez": company_info["Headquarters"]
                }
            },
        ]
    }
    r = requests.post(endpoint, json=data, headers=headers)
    return r.status_code == 200


def create_pdf(company_info):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    pdfmetrics.registerFont(TTFont('DejaVuSans', 'DejaVuSans.ttf'))

    logo_path = 'logo-2.png'
    logo_width = 150
    logo_height = 75
    logo_margin = 30

    logo_x = 50
    logo_y = height - logo_height - logo_margin

    c.drawImage(logo_path, logo_x, logo_y, width=logo_width, height=logo_height)

    c.setFont('DejaVuSans', 16)
    text_x = logo_x - 20
    y_position = logo_y - 40

    c.setFillColor(colors.darkblue)
    c.drawString(text_x, y_position, f"İsim: {company_info['Name']}")
    y_position -= 25

    c.setFont('DejaVuSans', 12)
    c.setFillColor(colors.black)
    c.drawString(text_x, y_position, f"URL: {company_info['URL']}")
    y_position -= 20
    c.drawString(text_x, y_position, f"Web Sitesi: {company_info['Website']}")
    y_position -= 20
    c.drawString(text_x, y_position, f"Alan: {company_info['Area']}")
    y_position -= 20

    c.setFillColor(colors.black)
    c.setFont('DejaVuSans', 12)
    c.drawString(text_x, y_position, "Açıklama:")
    y_position -= 15

    description_lines = wrap(company_info['Description'], width=90)
    for line in description_lines:
        c.drawString(text_x, y_position, line)
        y_position -= 15

    c.save()
    buffer.seek(0)
    return buffer

def main():
    st.title("LinkedIn Şirket Bilgileri Toplama")

    linkedin_username = st.text_input("LinkedIn Kullanıcı Adı")
    linkedin_password = st.text_input("LinkedIn Şifre", type="password")
    company_name = st.text_input("Şirket İsmi")
    company_url = st.text_input("Şirket URL (Opsiyonel)")
    search_button = st.button("Şirket Bilgilerini Ara")
    airtable_button = st.button("Airtable'a yükle")

    if 'driver' not in st.session_state:
        st.session_state.driver = None

    if 'collected_company_info' not in st.session_state:
        st.session_state.collected_company_info = None


    if search_button:
        if linkedin_username and linkedin_password and company_name:
            if not st.session_state.driver:
                options = Options()
                options.add_argument("--headless")  # Başsız tarayıcı
                options.add_argument("--no-sandbox")  # Sandbox'ı devre dışı bırak
                options.add_argument("--disable-dev-shm-usage")  # Paylaşılan bellek kullanımını devre dışı bırak
                service = Service(ChromeDriverManager().install())
                driver = webdriver.Chrome(service=service, options=options)
                driver.implicitly_wait(2)  # Bekleme süresi artırıldı
                st.session_state.driver = driver
                login_to_linkedin(driver, linkedin_username, linkedin_password)

            driver = st.session_state.driver

            if not company_url:
                company_url = f"https://www.linkedin.com/company/{company_name.lower()}/about/"

            company_info = get_company_info(driver, company_name, company_url)
            st.session_state.collected_company_info = company_info

            st.write("Şirket Bilgileri:")
            st.write(f"İsim: {company_info['Name']}")
            st.write(f"Linledin: {company_info['URL']}")
            st.write(f"Açıklama: {company_info['Description']}")
            st.write(f"Web Sitesi: {company_info['Website']}")
            st.write(f"Alan: {company_info['Area']}")
            st.write(f"Kuruluş Yılı: {company_info['Founded']}")
            st.write(f"Merkez: {company_info['Headquarters']}")
            st.write("-" * 40)

        else:
            st.error("Lütfen LinkedIn kullanıcı adı, şifre ve şirket ismi girin.")

    if st.session_state.collected_company_info:
        pdf_buffer = create_pdf(st.session_state.collected_company_info)
        # Şirket adını dosya adı olarak kullan
        sanitized_company_name = st.session_state.collected_company_info['Name'].replace(' ',
                                                                                         '_')
        st.download_button(
            label="PDF İndir",
            data=pdf_buffer,
            file_name=f"{sanitized_company_name}.pdf",  # Şirket adıyla dosya ismi
            mime="application/pdf"
        )

    if airtable_button:
        if not st.session_state.collected_company_info:
            st.error("Önce şirket bilgilerini toplayın.")
        else:
            success = add_to_airtable(st.session_state.collected_company_info)
            if success:
                st.success(f"{st.session_state.collected_company_info['Name']} başarıyla Airtable'a yüklendi.")
            else:
                st.error(f"{st.session_state.collected_company_info['Name']} Airtable'a yüklenirken hata oluştu.")

if __name__ == "__main__":
    main()
