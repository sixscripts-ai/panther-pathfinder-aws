from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import boto3

options = Options()
options.add_argument("--headless")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)




# Configuration
SUBJECT_CODES = ['ADJ']  # Testing with one subject first
TARGET_TERM = "Fall 2025"
OUTPUT_FILE = "expanded_courses.html"
S3_BUCKET = "ccc-summer-camp-2025-hartnell---panther-path-finder"  # <-- Replace this
S3_KEY = "hartnell/expanded_courses.html"
REGION = "us-west-2"

# Set up Selenium headless browser

print("Selenium WebDriver initialized.")

# Collect HTML
all_course_html = ""
expanded_count = 0
total_buttons = 0

for subject_code in SUBJECT_CODES:
    # Use dynamic subject code in URL
    url = f"https://stuserv.hartnell.edu/Student/Courses/Search?subjects={subject_code}"
    driver.get(url)
    print(f"Loading page for subject: {subject_code}")
    
    # Wait for page to load completely
    wait = WebDriverWait(driver, 15)
    
    try:
        # Wait for course results to load (check for the presence of course listings)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "ul.search-courselist, .search-coursedatarow")))
        print(f"Page loaded successfully for {subject_code}")
        
        time.sleep(2)  # Give time for any dynamic content to load
        
        # Select "Main Campus" location filter
        try:
            print("Looking for Main Campus location filter...")
            # Look for the Main Campus checkbox or toggle
            main_campus_elements = driver.find_elements(By.XPATH, "//input[@type='checkbox' and contains(@id, 'location') or contains(@name, 'location')]//following-sibling::label[contains(text(), 'Main Campus')] | //label[contains(text(), 'Main Campus')]//input[@type='checkbox']")
            
            if not main_campus_elements:
                # Try alternative selectors
                main_campus_elements = driver.find_elements(By.XPATH, "//input[contains(@id, 'Main') or contains(@value, 'Main')] | //label[contains(., 'Main Campus')]")
            
            if main_campus_elements:
                main_campus_element = main_campus_elements[0]
                # If it's a label, try to find the associated input
                if main_campus_element.tag_name == 'label':
                    input_elements = main_campus_element.find_elements(By.XPATH, ".//input[@type='checkbox'] | ./preceding-sibling::input[@type='checkbox'] | ./following-sibling::input[@type='checkbox']")
                    if input_elements:
                        main_campus_element = input_elements[0]
                
                # Check if it's already selected
                if main_campus_element.get_attribute("checked") != "true":
                    driver.execute_script("arguments[0].scrollIntoView(true);", main_campus_element)
                    time.sleep(0.5)
                    driver.execute_script("arguments[0].click();", main_campus_element)
                    print("✓ Selected Main Campus location filter")
                    time.sleep(2)  # Wait for filter to apply
                else:
                    print("✓ Main Campus filter already selected")
            else:
                print("⚠️ Main Campus location filter not found, continuing without filter")
        except Exception as e:
            print(f"⚠️ Error selecting Main Campus filter: {str(e)}, continuing without filter")
            time.sleep(1)
        
        # Find and expand all "View Available Sections" buttons
        section_buttons = driver.find_elements(By.CSS_SELECTOR, "button.esg-collapsible-group__toggle")
        print(f"Found {len(section_buttons)} section buttons to expand")
        total_buttons += len(section_buttons)
        
        expanded_in_this_subject = 0
        for i, btn in enumerate(section_buttons):
            try:
                # Check if this button contains "View Available Sections" text
                try:
                    span_text = btn.find_element(By.XPATH, ".//span[contains(text(), 'View Available Sections')]")
                    if span_text:
                        # Scroll the button into view and click it
                        driver.execute_script("arguments[0].scrollIntoView(true);", btn)
                        time.sleep(0.3)
                        
                        # Check if the button is already expanded (aria-expanded="true")
                        is_expanded = btn.get_attribute("aria-expanded") == "true"
                        if not is_expanded:
                            driver.execute_script("arguments[0].click();", btn)
                            expanded_count += 1
                            expanded_in_this_subject += 1
                            print(f"Expanded section {i+1}/{len(section_buttons)} for {subject_code}")
                            
                            # Simple wait for content to load
                            time.sleep(2)  # Wait for section data to load via AJAX
                        else:
                            print(f"Section {i+1}/{len(section_buttons)} already expanded for {subject_code}")
                except:
                    # This button doesn't have "View Available Sections" text, skip it
                    continue
                    
            except Exception as e:
                print(f"Failed to expand section {i+1} for {subject_code}: {str(e)}")
                continue
        
        print(f"✅ {subject_code}: Expanded {expanded_in_this_subject} out of {len(section_buttons)} sections")
        
        # Final wait for any remaining async operations
        print(f"Final wait for any remaining section data for {subject_code}...")
        time.sleep(3)  # Reduced final wait time
        
    except Exception as e:
        print(f"Error processing {subject_code}: {str(e)}")
        print("Continuing with current page content...")
    
    all_course_html += f"<!-- Subject: {subject_code} -->\n"
    all_course_html += driver.page_source + "\n\n"
    print(f"Collected HTML for subject: {subject_code}")

driver.quit()

print("✅ HTML collection complete.")
print(f"📊 Summary: Expanded {expanded_count} sections out of {total_buttons} total buttons across {len(SUBJECT_CODES)} subjects")

# Save to file
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write(all_course_html)

print(f"✅ HTML saved to {OUTPUT_FILE}")

# Upload to S3 with public-read ACL
try:
    s3 = boto3.client("s3", region_name=REGION)
    s3.upload_file(
        OUTPUT_FILE, S3_BUCKET, S3_KEY,
        ExtraArgs={'ContentType': 'text/html', 'ACL': 'public-read'}
    )

    print("✅ HTML uploaded to S3.")

    # Generate the public S3 URL
    s3_url = f"https://{S3_BUCKET}.s3.{REGION}.amazonaws.com/{S3_KEY}"
    print(f"✅ Upload complete. Your Bedrock Knowledge Base can ingest from:\n{s3_url}")

    print("s3 url generated:", s3_url)
except Exception as e:
    print(f"⚠️ S3 upload failed: {str(e)}")
    print("✅ HTML file saved locally only.")