import pandas as pd
import mysql.connector          
import streamlit as st  
import pytesseract
from pytesseract import Output
import cv2
import easyocr
import regex as re
from PIL import Image, ImageFont, ImageDraw                                      
import tempfile
import pathlib
from streamlit_option_menu import option_menu
import pytesseract
pytesseract.pytesseract.tesseract_cmd = 'D:\\GUVI\\Projects\\Project3\\Tesseract\\tesseract.exe'


def dataExtraction(image):
    column = {"Company Name": [], "Card Holders Name":[], "Designation":[], "Mobile Number":[], "Email Address":[],
          "Website URL":[], "Area":[], "City":[], "State":[], "Pincode":[], "Image":[]}
    reader = easyocr.Reader(["en"])
    result = reader.readtext(image, detail = 0)
    bName = ""
    p2 = r'^WWW$'
    p1 = r'^WWW(?=.*\.com)'
    p3 = r'\w+.com$'
    flag_toAdd = False
    flagOfAreaItem1 = False
    flagOfAreaItem2 = False
    flagToGetArea = False
    flagToGetCity = False
    flagToGetState = False
    var = ""
    only_www = ""
    rest_ofSite = ""
    varForACS= []
    mNum = ""

    cardHolderName = result[0]
    designation = result[1]
    column["Card Holders Name"].append(cardHolderName)
    column["Designation"].append(designation)
    
    with open(image, 'rb') as f:
        imageData = f.read()
    column['Image'].append(imageData)

    for i in range(2, len(result)):
      
        if re.findall(r'^[+]',result[i]):
            res = result[i]
            mNum = mNum +" , " + res
        elif(re.findall(r'^\d{3}-\d{3}-\d{4}$',result[i])):
            res = result[i]
            mNum = mNum + res

        elif (re.findall(r'[\w\.-]+@[\w\.-]+',result[i])):
            column["Email Address"].append(result[i])

        elif re.findall(r'^WWW(?=.*\.com)',result[i]):
            column["Website URL"].append(result[i])

        elif re.findall(r'^www(?=.*\.com)',result[i]):
            column["Website URL"].append(result[i])

        elif re.findall(r'^www(?=.*\scom)',result[i]):  #added s with com
            column["Website URL"].append(result[i])

        elif re.findall(p2,result[i]):
            only_www = result[i]
            flag_toAdd=True

        elif re.findall(p3,result[i]):
            rest_ofSite=result[i]
            flag_toAdd=True
                            
        elif re.findall(r'^\d{3}+\s+\w',result[i]):
            new=result[i].split(',')

            for item in new:
                if len(new) < 2:
                    if re.findall(r'^\d{3}+\s+\w',item):
                        var = item
                        flagOfAreaItem1 = True
        
                elif len(new) ==2: 
                    varForACS.append(item)
                       
                elif len(new) > 2:
                    varForACS.append(item)
                  
        elif re.findall("St",result[i]):
            new2=result[i].split(",")

            if(len(new2)<3):
                item2 = var+" "+result[i]
                flagOfAreaItem2 = True
        
            else:
                print("In else")
     
        elif re.findall('^\d{6}',result[i]):
            column["Pincode"].append(result[i])
          
        elif re.findall('\d{6}$',result[i]):
            state = []
            state.append(result[i].split(" "))
            column["State"].append(state[0][0])
            column["Pincode"].append(state[0][1])

        else:
            bName =bName+ " "+result[i]
    mNum=mNum.replace(",","",1)

    column["Mobile Number"].append(mNum)        
    if ',' in bName:
        SPL=bName.split(",")
        cityvar=SPL[0]
        column["City"].append(cityvar)
        flagToGetCity = True
        bName=SPL[1]

    column["Company Name"].append(bName)

    if flag_toAdd:
        webname=only_www+" "+rest_ofSite
        column["Website URL"].append(webname)

    if flagOfAreaItem1 and flagOfAreaItem2:
        column["Area"].append(item2)

    else:
        
        if len(varForACS) > 2:
            
            for item in varForACS:
                if len(item) < 2:
                    pass
                else:
                    if flagToGetArea == False:
                        areavar = item
                        column["Area"].append(areavar)
                        flagToGetArea = True
             
                    elif flagToGetCity == False:
                       
                        if ";" in item:
                            newItem = item.split(";")
                            cityvar = newItem[0]
                            statevar = newItem[1]
                            column["City"].append(cityvar)
                            column["State"].append(statevar)
                            flagToGetCity = True
                            flagToGetState = True

                        else:
                            cityvar = item
                            column["City"].append(cityvar)
                            flagToGetCity = True
                        
                    else:
                        flagToGetState == False
                        statevar = item
                        flagToGetState = True
                        column["State"].append(statevar)
                        break
   
        elif len(varForACS)==2:
            for item in varForACS:
                if len(item) < 2:
                    pass
                else:
                    
                    if flagToGetArea == False:
                        areavar = item
                        column["Area"].append(areavar)
                        flagToGetArea = True
              
                    elif flagToGetCity == False:
                        cityvar = item
                        column["City"].append(cityvar)
                        flagToGetCity = True
            
    return column

# #mysql connection
# Create an SQL connection
username = 'root'
password = '255244'
host = 'localhost'
database_name = 'BizCardX'

# Create the engine
mydb = mysql.connector.connect(
user=username,
password=password,
host=host,
database=database_name
)

if mydb.is_connected():
    print("connected to {database_name} database on {host}")
else:
    print("Connection failed")

cursor = mydb.cursor()

def cardDetailsToDb(mydb, cursor,dr):
    create_query = """CREATE TABLE IF NOT EXISTS BusinessCardDetails(CompanyName VARCHAR(30),
                                                                    CardHoldersName VARCHAR(20),
                                                                    Designation VARCHAR(20),
                                                                    MobileNumber VARCHAR(100),
                                                                    EmailAddress  VARCHAR(50),
                                                                    WebsiteURL VARCHAR(50),
                                                                    Area VARCHAR(50),
                                                                    City VARCHAR(30),
                                                                    State VARCHAR(50),
                                                                    Pincode BIGINT,
                                                                    Image LONGBLOB)"""

    cursor.execute(create_query)
    mydb.commit()

    for index, row in dr.iterrows():
        insert_query = """INSERT INTO BusinessCardDetails (CompanyName,
                                                            CardHoldersName,
                                                            Designation,
                                                            MobileNumber,
                                                            EmailAddress,
                                                            WebsiteURL,
                                                            Area,
                                                            City,
                                                            State,
                                                            Pincode,
                                                            Image)
                                                            values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
       
        values = (row["Company Name"],
                    row["Card Holders Name"],
                    row["Designation"],
                    row["Mobile Number"],
                    row["Email Address"],
                    row["Website URL"],
                    row["Area"],
                    row["City"],
                    row["State"],
                    row["Pincode"],
                    row["Image"]
                    )
        try:
            cursor.execute(insert_query, values)
            mydb.commit()
            st.write("Data inserted successfully")
        except Exception as e:
            print(f"Error inserting data: {e}")


#streamlit section
st.set_page_config(page_title="BizCardX", page_icon='🧊', layout = "wide")

page_background_color = """
<style>
[data-test-d ="stHeader]
{
background: rgba(0,0,0,0);
}
</style>"""

st.markdown(page_background_color, unsafe_allow_html=True)


# CREATING OPTION MENU
selected = option_menu(None, ["Home","Upload & Extract","Modify"],
                       icons=["house","cloud-upload","pencil-square"],
                       default_index=0,
                       orientation="horizontal",
                       styles={"nav-link": {"font-size": "35px", "text-align": "centre", "margin": "-2px", "--hover-color": "#6495ED"},
                               "icon": {"font-size": "35px"},
                               "container" : {"max-width": "6000px"},
                               "nav-link-selected": {"background-color": "#6495ED"}})

if selected == "Home":
    col1 , col2 = st.columns(2)
    with col1:
        st.image(Image.open("fabac5c3f0730a747c62e71e6ab6d18c.jpg"),width=500)
        st.markdown("## :green[**Technologies Used :**] Python,easy OCR, Streamlit, SQL, Pandas")
    with col2:
       st.write("## :green[**About :**] Bizcard is a Python application designed to extract information from business cards.")
       st.write('## The main purpose of Bizcard is to automate the process of extracting key details from business card images, such as the name, designation, company, contact information, and other relevant data. By leveraging the power of OCR (Optical Character Recognition) provided by EasyOCR, Bizcard is able to extract text from the images.')

if selected == "Upload & Extract":

    temp_dir = tempfile.TemporaryDirectory()
    uploaded_file = st.file_uploader("Choose a file")

    if uploaded_file is None:
        st.write("Upload a Business Card")

    if uploaded_file is not None:
        col1, col2 = st.columns(2)
        with col1:
            uploaded_file_path = pathlib.Path("D:\GUVI\\"+uploaded_file.name)
            with open(uploaded_file_path,"wb") as f: 
                f.write(uploaded_file.getbuffer())         
            st.image(uploaded_file,width = 650)
        
        with col2:
            img = cv2.imread(uploaded_file.name)
            d = pytesseract.image_to_data(img, output_type=Output.DICT)
            n_boxes = len(d['level'])
            for i in range(n_boxes):
                (x, y, w, h) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])
                cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
            st.image(img)
        
        if st.button("Click to Extract Data and save to Database"):
            r = dataExtraction(str(uploaded_file_path))
            dr = pd.DataFrame.from_dict(r, orient='index')
            dr = dr.transpose()
            db = cardDetailsToDb(mydb, cursor,dr)

        if st.button("View Database"):
            q = "select * from businesscarddetails"
            cursor.execute(q)
            result = cursor.fetchall()
            df = pd.DataFrame(result, columns = ["Company Name", "Card Holder's Name", "Designation", "Mobile Number","Email Address", "Website URL", "Area", "City", "State", "Pincode", "Image"])
            st.write(df)

if selected == "Modify":
    # st.subheader(':blue[You can view , alter or delete the extracted data in this app]')
    select = option_menu(None,
                         options=["ALTER", "DELETE"],
                         default_index=0,
                         orientation="horizontal",
                         styles={"container": {"width": "100%"},
                                 "nav-link": {"font-size": "20px", "text-align": "center", "margin": "-2px"},
    
                                 "nav-link-selected": {"background-color": "#6495ED"}})
   
    if select == "ALTER":
        st.subheader(":rainbow[Alter the data here]")
        try:
            cursor.execute("SELECT CardHoldersName FROM businesscarddetails")
            result = cursor.fetchall()
            business_cards = {}
            for row in result:
                business_cards[row[0]] = row[0]
            options = ["None"] + list(business_cards.keys())
            selected_card = st.selectbox("**Select a card**", options)
            # selected_option=options[0]
            if selected_card == "None":
                st.write("No card selected.")

            else:
                st.markdown("#### Update or modify any data below")
                q2 = "select CompanyName,CardHoldersName,Designation,MobileNumber,EmailAddress,WebsiteURL,Area,City,State,Pincode from businesscarddetails WHERE CardHoldersName='"+selected_card+"'" 
                cursor.execute(q2)
                result = cursor.fetchone()
                company_name = st.text_input("CompanyName", result[0],key="1")
                card_holder = st.text_input("CardHoldersName", result[1],key="2")
                designation = st.text_input("Designation", result[2],key="3")
                mobile_number = st.text_input("MobileNumber", result[3],key="4")
                email = st.text_input("EmailAddress", result[4],key="5")
                website = st.text_input("WebsiteURL", result[5],key="6")
                area = st.text_input("Area", result[6],key="7")
                city = st.text_input("City", result[7],key="8")
                state = st.text_input("State", result[8],key="9")
                pin_code = st.text_input("Pincode", result[9],key="0")
        
                if st.button(":blue[Commit changes to DB]"):
                    cursor.execute("""UPDATE businesscarddetails SET CompanyName=%s,CardHoldersName=%s,Designation=%s,MobileNumber=%s,EmailAddress=%s,WebsiteURL=%s,Area=%s,City=%s,State=%s,Pincode=%s
                                    WHERE CardHoldersName=%s""", (company_name, card_holder, designation, mobile_number, email, website, area, city, state, pin_code,
                    selected_card))
                    mydb.commit()
                    st.success("Information updated in database successfully.")
                if st.button(":blue[View updated data]"):
                    cursor.execute(
                        "select CompanyName,CardHoldersName,Designation,MobileNumber,EmailAddress,WebsiteURL,Area,City,State,Pincode from businesscarddetails")
                    updated_df = pd.DataFrame(cursor.fetchall(),
                                            columns=["Company_Name", "Card_Holder", "Designation", "Mobile_Number",
                                                    "Email",
                                                    "Website", "Area", "City", "State", "Pin_Code"])
                    st.write(updated_df)
        except:
            st.warning("There is no data available in the database.")
    if select == "DELETE":
        st.subheader(":rainbow[Delete the data]")
        try:
            cursor.execute("SELECT CardHoldersName FROM businesscarddetails")
            result = cursor.fetchall()
            business_cards = {}
            for row in result:
                business_cards[row[0]] = row[0]
            options = ["None"] + list(business_cards.keys())
            selected_card = st.selectbox("**Select a card**", options)
            if selected_card == "None":
                st.write("No card selected.")
            else:
                st.write(f"### You have selected :green[**{selected_card}'s**] card to delete")
                st.write("#### Proceed to delete this card?")
                if st.button("Yes Delete Business Card"):
                    cursor.execute(f"DELETE FROM businesscarddetails WHERE CardHoldersName='{selected_card}'")
                    mydb.commit()
                    st.success("Business card information deleted from database.")

            if st.button(":blue[View updated data]"):
                cursor.execute(
                    "select CompanyName,CardHoldersName,Designation,MobileNumber,EmailAddress,WebsiteURL,Area,City,State,Pincode from businesscarddetails")
                updated_df = pd.DataFrame(cursor.fetchall(),
                                          columns=["Company_Name", "Card_Holder", "Designation", "Mobile_Number",
                                                   "Email",
                                                   "Website", "Area", "City", "State", "Pin_Code"])
                st.write(updated_df)

        except:
            st.warning("There is no data available in the database")
    



   
