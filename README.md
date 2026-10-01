SETUP

1. Populate backend/data with your PDF data
2. Run the following commands

   cd .\rag-ai\backend\
   .\venv\Scripts\Activate.ps1
   python fill_db.py
   
This will activate the python virtual environment and fill the DB with your vectorised and chunked data.

3. Run the follwing commands
   cd ..\frontend\
   npm run dev

4. Open the local -> In your browser
   
