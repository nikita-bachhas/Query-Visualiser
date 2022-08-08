# Query-Visualiser
The Query Visualiser takes in a query as an input and outputs the most efficient query execution plan

## Functionality
1. Generated and created a set of queries using the TPC-H benchmark data and queries
2. Designed and implemented a GUI that takes in a query as an input, retrieves its query execution plan and outputs the query execution plan in natural language.

## Documentation
All documents can be found under the [Documentation](https://github.com/nikita-bachhas/Query-Visualiser/tree/main/Documentation) folder
1. Full details of the project: [CZ4031 Project 2 Report.pdf](https://github.com/nikita-bachhas/Query-Visualiser/blob/main/Documentation/CZ4031%20Project%202%20Report.pdf)

## Requirements:
- database should be in PostgreSQL
- ensure dependencies in requirements.txt are installed

## To run the database on default TPC-H:
- run the .sql files in scripts\create_scripts
- open _Command Prompt in Windows/Linux_ or _Terminal in MacOS_
- navigate to the root directory of the program
- enter the following command:

`python project.py` 

- You should see a window that prompts for the password and other relevant database information
- By <b>default</b>, hostname = "localhost", username = "postgres" and port id = "5432" and thus can be left BLANK
- Enter confirm and if the input information is correct, another window will appear with the text box for the user input query.
- Enter the query and click "Show" which will output the query plan below.
- Click "Generate Query Plan" to obtain a graph of the query execution plan, this will be stored as a .png file in the same directory. 
- "Next Query" will open a new window which will prompt users to input their database information again and their query.

## Developed by
1. Bachhas Nikita
2. Kam Chin Voon
3. Kundu Koushani
