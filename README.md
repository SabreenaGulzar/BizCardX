# BizCardX: Extracting Business Card Data with OCR

Bizcard is a Python application designed to ectract information from business cards.
The main purpose of Bizcard is to automate the process of ectracting key details from business card images, such as the name, designation, company and other relevant data.
By levaraging the power of OCR(Optical Character Recognition) provided by EasyOCR, Bizcard is able to extract text from the images.

Technologies used:
1. Python
2. EasyOCR
3. Streamlit
4. SQL
5. Pandas

Approach:
1. Install the required packages.
2. Design the user interface: Create a simple and intuitive user interface using Streamlit that guides users through the process of uploading the business card image and extracting its information.
3. Implement the image processing and OCR: Use easyOCR to extract the relevant information from the uploaded business card image. You can use image processing techniques like resizing, cropping, and thresholding to enhance the image quality before passing it to the OCR engine.
4. Display the extracted information: Once the information has been extracted, display it in a clean and organized manner in the Streamlit GUI. You can use widgets like tables, text boxes, and labels to present the information.
5. Implement database integration: Use a database management system like SQLite or MySQL to store the extracted information along with the uploaded business card image. You can use SQL queries to create tables, insert data, and retrieve data from the database, Update the data and Allow the user to delete the data through the streamlit UI.


Contact: https://www.linkedin.com/in/sabreena-gulzar-5a0227176/
