from altair import Column
import cv2
import easyocr
import matplotlib.pyplot as plt
import numpy as np 
import regex as re
import pandas as pd
import mysql.connector          
import streamlit as st  
from PIL import Image, ImageFont, ImageDraw                                      
from pathlib import Path

def dataExtraction(image):
    column = {"Company Name": [], "Card Holders Name":[], "Designation":[], "Mobile Number":[], "Email Address":[],
          "Website URL":[], "Area":[], "City":[], "State":[], "Pincode":[], "Image":[]}
    reader = easyocr.Reader(["en"])
    result = reader.readtext(image, detail = 0)
    #st.write(result)
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
    # # # with open(image, encoding="utf8", errors='ignore') as f:
        imageData = f.read()
        #st.write(imageData)
    column['Image'].append(imageData)

    for i in range(2, len(result)):
        print("RESULT>>>>",result[i])

        if re.findall(r'^[+]',result[i]):
            res = result[i]
            st.write("value of result",res)
            mNum = mNum +" , " + res
            st.write("Value of mNum", mNum)
            # column["Mobile Number"]= mNum

        elif(re.findall(r'^\d{3}-\d{3}-\d{4}$',result[i])):
            res = result[i]
            st.write("value of result",res)
            mNum = mNum + res
            #column["Mobile Number"]= mNum

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
    st.write("MOBILE",mNum)
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



                 
# imageExtractedData = pd.DataFrame(dataExtraction("2.png"))
# print(imageExtractedData)

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
    st.write("Start table creation if not exists")
    create_query = """CREATE TABLE IF NOT EXISTS BusinessCardDetails(CompanyName VARCHAR(30),
                                                                    CardHoldersName VARCHAR(20),
                                                                    Designation VARCHAR(20),
                                                                    MobileNumber VARCHAR(100),
                                                                    EmailAddress  VARCHAR(50) Primary key,
                                                                    WebsiteURL VARCHAR(50),
                                                                    Area VARCHAR(50),
                                                                    City VARCHAR(30),
                                                                    State VARCHAR(50),
                                                                    Pincode BIGINT,
                                                                    Image LONGBLOB)"""

    cursor.execute(create_query)
    mydb.commit()
    print("Table is created")

    st.write("Start data insertion in table")
    # st.write("prinitng dr",dr)
    for index, row in dr.iterrows():
        # st.write("index and row", index, row)
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
        # st.write(insert_query)
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

st.set_page_config(page_title="BizCardX", page_icon='🧊', layout = "wide")

page_background_color = """
<style>
[data-test-d ="stHeader]
{
background: rgba(0,0,0,0);
}
</style>"""

st.markdown(page_background_color, unsafe_allow_html=True)




temp_dir = tempfile.TemporaryDirectory()
st.write(temp_dir.name)
uploaded_file = st.file_uploader("Choose a file")

uploaded_file_path = pathlib.Path("D:\GUVI\\"+uploaded_file.name)
st.write("UFP",uploaded_file_path)
st.write(uploaded_file)
if uploaded_file is not None:


    with open(uploaded_file_path,"wb") as f: 
        f.write(uploaded_file.getbuffer())         
        st.success("Saved File")
        st.write("FILE_PATH>>>",uploaded_file_path)
        st.write(uploaded_file_path)
        type(uploaded_file_path)

    r = dataExtraction(str(uploaded_file_path))
    st.write("printing r", r)
   
    dr = pd.DataFrame.from_dict(r, orient='index')
    dr = dr.transpose()
    st.write("DATA dr ",dr)
    st.write("Calling MYSQL")
    cardDetailsToDb(mydb, cursor,dr)



    

   
