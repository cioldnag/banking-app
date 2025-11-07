@ECHO OFF
set root=c:\banking_2
call %root%\Scripts\activate.bat
cd c:\users\loicg\OneDrive\Documents\IT\banking
call streamlit run app_bank.py