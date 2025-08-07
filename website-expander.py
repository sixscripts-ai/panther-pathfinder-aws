from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
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
TARGET_TERM = "Fall 2025"
S3_BUCKET = "ccc-summer-camp-2025-hartnell---panther-path-finder"  # <-- Replace this
REGION = "us-west-2"

# Set up Selenium headless browser

print("Selenium WebDriver initialized.")

# Process all courses (no subject filter)
print(f"\n🎯 Processing all courses")

# Create filename for all courses
output_file = f"expanded_courses_all.html"
s3_key = f"hartnell/expanded_courses_all.html"

# Initialize HTML collection
subject_html = ""
expanded_count = 0
total_buttons = 0

# Use default search URL to get all courses
url = "https://stuserv.hartnell.edu/Student/Courses/Search?"
driver.get(url)
print(f"Loading all courses page")

# Wait for page to load completely
wait = WebDriverWait(driver, 15)
    
try:
    # Wait for course results to load (check for the presence of course listings)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "ul.search-courselist, .search-coursedatarow")))
    print(f"Page loaded successfully for all courses")
    
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
    
    # Check for pagination and get total pages
    current_page = 1
    total_pages = 1
    
    try:
        # Wait for pagination to load
        wait.until(EC.presence_of_element_located((By.ID, "paging")))
        total_pages_element = driver.find_element(By.ID, "course-results-total-pages")
        total_pages = int(total_pages_element.text.strip())
        print(f"📄 Found {total_pages} page(s) for all courses")
    except:
        print(f"📄 Single page detected for all courses")
    
    # Process each page
    for page_num in range(1, total_pages + 1):
        print(f"\n📄 Processing page {page_num}/{total_pages}")
        
        # Navigate to the specific page (if not already on it)
        if page_num > 1:
            try:
                # Enter the page number in the input field
                page_input = driver.find_element(By.ID, "course-results-current-page")
                page_input.clear()
                page_input.send_keys(str(page_num))
                
                # Press Enter or trigger the page change
                page_input.send_keys(Keys.RETURN)
                
                # Wait for the page to load
                time.sleep(3)
                print(f"✓ Navigated to page {page_num}")
            except Exception as e:
                print(f"⚠️ Error navigating to page {page_num}: {str(e)}")
                continue
        
        # Find and expand all "View Available Sections" buttons on this page
        section_buttons = driver.find_elements(By.CSS_SELECTOR, "button.esg-collapsible-group__toggle")
        page_buttons = len(section_buttons)
        total_buttons += page_buttons
        print(f"Found {page_buttons} section buttons to expand on page {page_num}")
        
        expanded_in_this_page = 0
        for i, btn in enumerate(section_buttons):
            try:
                # Check if this button contains "View Available Sections for" text (more specific)
                try:
                    span_text = btn.find_element(By.XPATH, ".//span[starts-with(text(), 'View Available Sections for')]")
                    if span_text:
                        # Scroll the button into view and click it
                        driver.execute_script("arguments[0].scrollIntoView(true);", btn)
                        time.sleep(0.3)
                        
                        # Check if the button is already expanded (aria-expanded="true")
                        is_expanded = btn.get_attribute("aria-expanded") == "true"
                        if not is_expanded:
                            driver.execute_script("arguments[0].click();", btn)
                            expanded_count += 1
                            expanded_in_this_page += 1
                            
                            # Get the course name from the span text for better logging
                            course_name = span_text.text.replace("View Available Sections for ", "")
                            print(f"Expanded section for {course_name} ({i+1}/{page_buttons}) on page {page_num}")
                            
                            # Simple wait for content to load
                            time.sleep(2)  # Wait for section data to load via AJAX
                        else:
                            course_name = span_text.text.replace("View Available Sections for ", "")
                            print(f"Section for {course_name} ({i+1}/{page_buttons}) already expanded on page {page_num}")
                except:
                    # This button doesn't have "View Available Sections for" text, skip it
                    continue
                    
            except Exception as e:
                print(f"Failed to expand section {i+1} on page {page_num}: {str(e)}")
                continue
        
        print(f"✅ Page {page_num}: Expanded {expanded_in_this_page} out of {page_buttons} sections")
        
        # Add page content to subject HTML
        subject_html += f"<!-- Page {page_num} of {total_pages} for All Courses -->\n"
        subject_html += driver.page_source + "\n\n"
    
    print(f"✅ All Courses: Expanded {expanded_count} sections across {total_pages} page(s)")
    
    # Final wait for any remaining async operations
    print(f"Final wait for any remaining section data...")
    time.sleep(3)  # Reduced final wait time
    
except Exception as e:
    print(f"Error processing all courses: {str(e)}")
    print("Continuing with current page content...")
    # If there's an error, still collect what we have
    subject_html += f"<!-- Error occurred, partial content for All Courses -->\n"
    subject_html += driver.page_source + "\n\n"

print(f"Collected HTML for all courses")

# Save to file
with open(output_file, "w", encoding="utf-8") as f:
    f.write(subject_html)
print(f"✅ HTML saved to {output_file}")

# Upload to S3 with public-read ACL
try:
    s3 = boto3.client("s3", region_name=REGION)
    s3.upload_file(
        output_file, S3_BUCKET, s3_key,
        ExtraArgs={'ContentType': 'text/html', 'ACL': 'public-read'}
    )

    print(f"✅ HTML uploaded to S3 as {s3_key}")

    # Generate the public S3 URL
    s3_url = f"https://{S3_BUCKET}.s3.{REGION}.amazonaws.com/{s3_key}"
    print(f"✅ Upload complete. URL: {s3_url}")

except Exception as e:
    print(f"⚠️ S3 upload failed: {str(e)}")
    print(f"✅ HTML file saved locally as {output_file}")

print(f"✅ All Courses: Expanded {expanded_count} sections out of {total_buttons} total buttons")

driver.quit()

print("✅ All courses processed successfully!")
print(f"📁 HTML file created: {output_file}")
print(f"☁️ File uploaded to S3 bucket: {S3_BUCKET}")
print("🎯 Ready for Bedrock Knowledge Base ingestion")