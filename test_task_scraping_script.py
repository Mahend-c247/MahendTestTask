# Importing all libraries
import json
import time
import pandas as pd
from time import sleep
from faker import Faker
from pymongo import MongoClient
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

json_data = {"chapter-living": []}

Room_number_list = []
building_list = []
rent_list = []
deposit_list = []
amenities_list = []
space_list = []
status_list = []
payment_plan_options_list = []



# created a def function for form filling
def formfill():
    fake = Faker()
    FName = driver.find_element(By.ID, "applicant_first_name")
    FName.send_keys(fake.name())

    LName = driver.find_element(By.ID, "applicant_last_name")
    LName.send_keys(fake.name())

    C_code = driver.find_element(By.XPATH, "//input[@class='country-code']")
    C_code.clear()
    C_code.send_keys("+91")

    fake = Faker('en_IN')
    indian_phone_number = fake.phone_number()
    indian_phone_number = indian_phone_number.replace(" ", "")
    number = indian_phone_number
    num = driver.find_element(By.XPATH, "//input[@class='phone-number']")
    num.send_keys(number)

    Email_ID = driver.find_element(By.ID, "applicant_username")
    email_id = fake.name()[:3] + number[:3] + '@gmail.com'
    Email_ID.send_keys(email_id)

    password_str = f'{number[:4]}2023@@#'
    password = driver.find_element(By.ID, "applicant_password")
    password.send_keys(password_str)

    Confirm_P = driver.find_element(By.ID, "applicant_password_confirm")
    Confirm_P.send_keys(password_str)

    # Wait for the agree_button to be clickable
    wait = WebDriverWait(driver, 15)
    agree_button = wait.until(EC.element_to_be_clickable((By.ID, "agrees_to_terms")))

    # Scroll into view
    driver.execute_script("arguments[0].scrollIntoView();", agree_button)

    # Click the agree_button
    agree_button.click()

    sleep(5)
    Confirm_P.send_keys(Keys.ENTER)
    sleep(10)
    driver.find_element(By.XPATH, "//a[@class='btn btn--full js-confirm']").click()

# created a def function for extracting all Room Data
def Room_details():
    time.sleep(5)
    l = driver.find_elements(By.XPATH, '//*[@id="unit-details-section"]/div/div')
    for i in range(1, len(l) + 1):
        try:
            time.sleep(7)
            unit_space_details = driver.find_element(By.XPATH, f'//*[@id="unit-details-section"]/div/div[{str(i)}]')
            driver.execute_script("arguments[0].scrollIntoView();", unit_space_details)

            # Extract Room number 
            number = unit_space_details.find_element(By.TAG_NAME, "h6").text.strip()
            Room_number_list.append(number)

            # Extract building
            building = unit_space_details.find_element(By.XPATH, ".//dt[text()='Building']/following-sibling::dd").text.strip()
            building_list.append(building)

            # Extract rent
            rent = unit_space_details.find_element(By.XPATH, ".//dt[text()='Rent']/following-sibling::dd").text.strip()
            rent_list.append(rent)

            # Extract deposit 
            deposit = unit_space_details.find_element(By.XPATH, ".//dt[text()='Deposit']/following-sibling::dd").text.strip()
            deposit_list.append(deposit)

            # Extract amenities
            amenities = unit_space_details.find_element(By.XPATH, ".//div[dt[@class='title' and text()='Amenities']]/dd[@class='value']").text
            amenities_list.append(amenities)

            # Extract space
            space_table = driver.find_element(By.CLASS_NAME, "unit-space-table")
            space_row = space_table.find_element(By.XPATH, ".//tbody/tr")
            space = space_row.find_element(By.XPATH, ".//td[2]").text
            space_list.append(space)
            
            # Extract status  
            status = space_row.find_element(By.XPATH, ".//td[3]").text
            status_list.append(status)

            # Extract payment plan options 
            payment_option_container = driver.find_element(By.CLASS_NAME, "payment-option-container")
            plan_options_list = payment_option_container.find_element(By.CLASS_NAME, "js-field-toggler")
            plan_items = plan_options_list.find_elements(By.CLASS_NAME, "radio-group-item")
            payment_plan_options = [item.find_element(By.XPATH, ".//span").text for item in plan_items]
            payment_plan_options_list.append(payment_plan_options)

        except Exception as e:
            print(f"Error processing element {i}: {e}")
            continue


# Driver
driver = webdriver.Chrome()
driver.maximize_window()
driver.get('https://www.chapter-living.com/')

# Click Book A Room button
driver.find_element(By.XPATH, "//a[@id='btn-main-book-a-room-pink']").click()
time.sleep(5)
driver.find_element(By.XPATH, '//*[@id="BookingAvailabilityForm_Residence"]/option[7]').click()
time.sleep(7)
driver.find_element(By.XPATH, '//*[@id="BookingAvailabilityForm_BookingPeriod"]/option[2]').click()
time.sleep(7)


# Click Bronze Ensuite apply buttton
Bronze_Ensuite = driver.find_element(By.XPATH, '//*[@id="modal-room-3"]/div[4]/div/div[2]/a/span')
Room_type = driver.find_element(By.XPATH, f'//*[@id="modal-room-3"]/div[4]/div/p[2]/strong').text.strip()
time.sleep(5)
driver.execute_script("window.scrollTo(0, 1700);")
# driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
Bronze_Ensuite.click()
time.sleep(10)

# Function Call
formfill()
Room_details()
print(json_data)


# Print the extracted information
print(f"Room{Room_number_list}")
print(f"Building = {building_list}")
print(f"Rent = {rent_list}")
print(f"Deposit = {deposit_list}")
print(f"Amenities = {amenities_list}")
print(f"Space = {space_list}")
print(f"Status = {status_list}")
print(f"Select a Payment Plan Option = {payment_plan_options_list}")

# Create DataFrame
data={"Room_number":Room_number_list,"building":building_list,
      "rent":rent_list,"deposit":deposit_list,"amenities":amenities_list,
      "space":space_list,"status":status_list,"payment_plan_options":payment_plan_options_list}

df=pd.DataFrame(data)
print(df)

# Dataframe to Json
df_json_data = df.to_json(orient='records')
data_dict = json.loads(df_json_data)
json_data['chapter-living'].append({Room_type: data_dict})
print(json_data)

# MongoDB Atlas connection string
uri = "mongodb+srv://Mahend_Verma:MahendC247@c247.i467onm.mongodb.net/?retryWrites=true&w=majority"

# Create a new client and connect to the server
client = MongoClient(uri)

# Specify the database and collection
db = client["chapter-living"]
collection = db["TestTask"]


# Insert JSON data into MongoDB (assuming it's a single document)
collection.insert_one(json_data)

# Close the MongoDB connection
client.close()

print("Data loaded successfully.")


