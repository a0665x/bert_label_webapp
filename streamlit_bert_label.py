import streamlit as st
import json
import os
import pandas as pd
from st_aggrid import AgGrid
from utils.tool_funs import BlobDataTransaction , NoLoggingPolicy
def add_bg_from_local(image_file):
    with open(image_file, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
    st.markdown(f"""
    <style>
    .stApp {{
        background-image: url(data:image/{"png"};base64,{encoded_string.decode()});
        background-size: cover
    }}
    </style>
    """,
        unsafe_allow_html=True)

add_bg_from_local('./background.jpg')
st.set_page_config(layout="wide")
#========================================================================
Login_Flag = None
# st.set_page_config(layout="wide")
st.sidebar.title("Azure Blob Storage Login")
USER = st.sidebar.text_input("Label User:" , value="")
storage_account_name = st.sidebar.text_input("Storage Account Name:", value="nlplabel")
storage_account_key = st.sidebar.text_input("Storage Account Key:", type="password", value="8O4CcWidAmAv+sFdraQ6VTsANHgiutP2mlbWBex41vPyxKgkLVfE4W71GUVsPOqcKWo76AmhkG1a+AStfEUeFA==")
container_name = st.sidebar.text_input("Container Name:", value="labelfile")
connection_string = f"DefaultEndpointsProtocol=https;AccountName={storage_account_name};AccountKey={storage_account_key};EndpointSuffix=core.windows.net"
@st.cache(allow_output_mutation=True)
def login(USER,storage_account_name, storage_account_key, container_name ):
    connection_string = f"DefaultEndpointsProtocol=https;AccountName={storage_account_name};AccountKey={storage_account_key};EndpointSuffix=core.windows.net"
    DT = BlobDataTransaction('', '', connection_string, container_name)
    return DT
if st.sidebar.button('Login'):
    DT = login(USER , storage_account_name, storage_account_key, container_name)
    Login_Flag = True
    if Login_Flag:
        st.sidebar.write('Already Login')
DT = login(USER,storage_account_name, storage_account_key, container_name)
st.sidebar.write("""***""")
#========================================================================
SAVE_PATH = './Temp/label_data/'
PROMPT_PATH = './Temp/prompt/'
if os.path.exists(SAVE_PATH) is not True:
    os.makedirs(SAVE_PATH)
if os.path.exists(PROMPT_PATH) is not True:
    os.makedirs(PROMPT_PATH)
st.header('NLP label tools')
label_style = st.sidebar.selectbox('What semantic annotation do you need to process?' , ('','binary_level','level_self_defined','context_prompt'))
label_json = {}
st.sidebar.write("""***""")
if label_style == 'binary_level':
    assign_label   = st.sidebar.selectbox('🏷️ Assign the context label',['0','1'])
if label_style == 'level_self_defined':
    label_num = st.sidebar.number_input('Setting total number of labels:',min_value = 0 , max_value=99 , step=1 )
    assign_label = st.sidebar.selectbox('Choose the designated level number.: ', range(2 if label_style == 'binary_level' else label_num if label_style == 'level_self_defined' else 2))
if label_style == 'level_self_defined' or label_style == 'binary_level':
    label_descript = st.sidebar.text_area('Write the context description')
    file_check = os.path.exists(SAVE_PATH + f"{USER}_label.json")
    st.sidebar.write(f'path_check:{file_check} ||'+SAVE_PATH + f"{USER}_label.json")
    if  file_check == False:

        with open(SAVE_PATH + f"{USER}_label.json", "w",encoding='utf-8') as outfile:
            json.dump({'label_style': label_style}, outfile)
    submitted = st.sidebar.button("📥 upload_label_description")
    if submitted:
        st.write(f"label:{assign_label}:{label_descript}")
        with open(SAVE_PATH + f"{USER}_label.json", "r",encoding='utf-8') as file:
            label_json = json.load(file)
            label_json[assign_label] = label_descript
        with open(SAVE_PATH + f"{USER}_label.json", "w",encoding='utf-8') as outfile:
            json.dump(label_json, outfile)
        st.sidebar.write('json path:'+SAVE_PATH +f"{USER}_label.json")

    with open(SAVE_PATH +f"{USER}_label.json", "r", encoding='utf-8') as file:
        label_json = json.load(file)
    st.sidebar.json(label_json)
    if st.sidebar.button('upload_json_to_Azure'):
        DT.uploadJsonObjToBlobStorage(label_json , f'{USER}_label.json')

    st.sidebar.write('<style>div.row-widget.stRadio > div{flex-direction:row;justify-content: center;} </style>',
             unsafe_allow_html=True)
    st.sidebar.write('<style>div.st-bf{flex-direction:column;} div.st-ag{font-weight:bold;padding-left:2px;}</style>',
             unsafe_allow_html=True)
    cancel = st.sidebar.radio('are you sure to cancel all label file?[Y/N]:', ('No' , 'Yes'))

    if st.sidebar.button('🧹 Reset_json_kernel') and cancel == 'Yes':
        try:
            DT.removeDataFromBlob(SAVE_PATH + f"{USER}_label.json")
            os.remove(SAVE_PATH + f"{USER}_label.json")
        except:
            st.sidebar.write('There is no data in the local or cloud storage')
            pass

    col1, col2 = st.columns([7,3],gap="large")
    #=====================================================
    with col1:
        st.write("Assign the context label")
        st.write('<style>div.row-widget.stRadio > div{flex-direction:row;justify-content: center;} </style>',
                unsafe_allow_html=True)
        st.write('<style>div.st-bf{flex-direction:column;} div.st-ag{font-weight:bold;padding-left:2px;}</style>',
                unsafe_allow_html=True)

        slider_val = st.radio("🏷️ Label:",range(2 if label_style == 'binary_level' else label_num if  label_style == 'level_self_defined' else 0))
        try:
            with open(SAVE_PATH + f"{USER}_label.json", "r",encoding='utf-8') as file:
                label_json = json.load(file)

            show_discription = label_json[str(slider_val)]
        except:
            show_discription = 'Please write the description in the left sidebar'
        with st.form("myform",clear_on_submit=True):
            st.write('discription:',show_discription)
            nlp_context = st.text_area('🗣️ write NLP label context on below✍🏻️:').replace('\n','')
            # Every form must have a submit button.
            # submitted = st.button("💌 Submit",on_click=clear_form)
            submitted = st.form_submit_button("💌 Submit")
            if submitted:
                if os.path.exists(SAVE_PATH + f"{USER}_NLP_dataset.csv")==False:
                    try:
                        DT.downloadFileFromBlobStorage(f"{USER}_NLP_dataset.csv" , SAVE_PATH + f"{USER}_NLP_dataset.csv")
                    except:
                        pass
                st.write("previous saved:\n", f'label:{slider_val} , context:{nlp_context}')
                with open(SAVE_PATH + f"{USER}_NLP_dataset.csv", "a+",encoding='utf-8') as csv_file:
                    csv_file.write(str(slider_val)+','+nlp_context+'\n')
                st.write("csv_path:"+SAVE_PATH +f"{USER}_NLP_dataset.csv")
        st.write("""***""")

        if os.path.exists(SAVE_PATH + f"{USER}_NLP_dataset.csv"):
            with open(SAVE_PATH + f"{USER}_NLP_dataset.csv", "r",encoding= 'utf-8') as csv_file:
                lines = csv_file.readlines()[-3:]
            df = pd.DataFrame(columns = ['label','context'])
            for line in lines:
                df1 = pd.DataFrame([[line[0] , line[2:]]],columns=['label', 'context'])
                df = df.append(df1)
            # st.dataframe(df)
            st.write("show last 3 rows of label:")
            AgGrid(df,theme='dark',  # Add theme color to the table
                        enable_enterprise_modules=True,
                        height=200,
                        reload_data=False,
                        wrap_text=True,
                        resizeable=True)

        if st.button('csv_to_Azure'):
            DT.uploadToBlobStorage(SAVE_PATH + f"{USER}_NLP_dataset.csv" ,  f"{USER}_NLP_dataset.csv")
        st.write("""***""")

        cancel_csv = st.radio('are you sure to cancel all csv file?[Y/N]:', ('No', 'Yes'))
        if st.button('🧹 reset_csv_kernel') and cancel_csv == 'Yes':
            try:
                DT.removeDataFromBlob(SAVE_PATH + f"{USER}_NLP_dataset.csv")
                os.remove(SAVE_PATH + f"{USER}_NLP_dataset.csv")
            except:
                df = pd.DataFrame(columns=['label', 'context'])
                st.write('The CSV file has already been cancelled.')
    with col2:
        uploaded_files = st.file_uploader("Choose a txt file", accept_multiple_files=True)
        for uploaded_file in uploaded_files:
            # bytes_data = uploaded_file.read()
            # st.write("filename:", uploaded_file.name)
            # st.write(bytes_data)
            with open(PROMPT_PATH +uploaded_file.name,'r',encoding='utf-8') as path:
                text = path.read()
            st.write(f'prompt txt:{uploaded_file.name}')
            st.write(text , encoding='utf-8')


if label_style == 'context_prompt':
    label_num = st.sidebar.number_input('setting total number of action:',min_value = 0 , max_value=99 , step=1)
    label_descript = st.sidebar.text_area('write the context description')
    st.header('😵 Allen_Huang is still designing the details of the labeling function, or you can buy him a coffee to console him 🔨🔨')

    pass


hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)


#streamlit run streamlit_bert_label.py --server.address 127.0.1.2 --server.port 80

# pakage to exe
# step1: upload projectfile to github
# https://github.com/a0665x/Bert_Label_tool
# setp2: go cloud streamlite and sign in by Github ID
# https://streamlit.io/cloud
# step3: choose py project for deploy and cook in oven process
# step4: copy the web address (ex:https://a0665x-bert-label-tool-streamlit-bert-label-7mgm9w.streamlit.app/)
# step5: install nativefier by using nmp install
# npm install -g nativefier
# step6: run cmd to packing
# nativefier --name '<you .exe name>' '<your streamlit sharing website url>' --platform < 'windows' or 'mac' or 'linux' >
# nativefier --name NLP_label_tool https://a0665x-bert-label-tool-streamlit-bert-label-uh7qs6.streamlit.app/ --platform windows --single-instance

# or npm install -g appnativefy (for ubuntu)
# appnativefy --name NLP_label_tool --url https://a0665x-bert-label-tool-streamlit-bert-label-7mgm9w.streamlit.app/ --services

#nativefier --arch "x64" --platform "windows" --icon "C:\Users\User\PycharmProjects\bert_emot\project_demo\bert_label_tool\bert_emot.ico" --name "bert_emot_tool" "https://a0665x-bert-label-tool-streamlit-bert-label-uh7qs6.streamlit.app/" –-maximize –-always-on-top –-clear-cache –app-copyright "Allen_Huang" --app-version 1 –-disable-dev-tools –-tray "C:\Users\User\PycharmProjects\bert_emot\project_demo\bert_label_tool"