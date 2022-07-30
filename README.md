# Requirements:

- database should be in PostgreSQL
- ensure dependencies in requirements.txt are installed

# To run database on default TPC-H:

- run the .sql files in scripts\create_scripts
- open _Command Prompt in Windows/Linux_ or _Terminal in MacOS_
- navigate to root directory of program
- enter command:

`python project.py` 

- You should see a window that prompts for the password and other relevant database information
- By <b>default</b>, hostname = "localhost", username = "postgres" and port id = "5432" and thus can be left BLANK
- Enter confirm and if the input information are correct, another window will appear with the text box for user input query.
- Enter query and click "Show" which will output the query plan below.
- Click "Generate Query Plan" to obtain a graph of the query execution plan, this will be stored as a .png file in the same directory. 
- "Next Query" will open a new window which will prompt user to input their database information again and their query.
