# l_scraper

This Streamlit application allows users to collect company information from LinkedIn and store it in Airtable. It also generates a PDF report for each company.

## Prerequisites

- Python 3.7 or higher
- Chrome browser installed

## Setup

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/l_scraper.git
   cd l_scraper
   ```

2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the root directory of the project and add your credentials:
   ```
   LINKEDIN_USERNAME=your_linkedin_username
   LINKEDIN_PASSWORD=your_linkedin_password
   AIRTABLE_BASE_ID=your_airtable_base_id
   AIRTABLE_API_TOKEN=your_airtable_api_token
   AIRTABLE_TABLE_NAME=your_airtable_table_name
   ```

## Usage

1. Run the Streamlit app:
   ```
   streamlit run main.py
   ```

2. Open your web browser and go to the URL provided by Streamlit (usually http://localhost:8501).

3. Enter the company name and optionally the company URL in the input fields.

4. Click "Şirket Bilgilerini Ara" to fetch the company information.

5. Click "PDF İndir" to download a PDF report of the company information.

6. Click "Airtable'a yükle" to upload the company information to Airtable.

## Notes

- The application uses Selenium WebDriver to scrape LinkedIn. It runs Chrome in headless mode, so you won't see the browser window open.
- Make sure your LinkedIn credentials are correct and that you have the necessary permissions to access company information.
- Ensure your Airtable API key has the correct permissions to write to the specified base and table.

## Troubleshooting

If you encounter any issues:

1. Make sure all the required packages are installed correctly.
2. Check that your `.env` file contains the correct credentials.
3. Ensure you have a stable internet connection.
4. If you're having issues with Chrome, try updating to the latest version.

## Contributing

Feel free to fork this repository and submit pull requests with any improvements or bug fixes.

## License

This project is licensed under the MIT License.
