from preprocess import *
import tkinter as tk
from tkinter import *
import os
import sys
from networkx.classes import graph
import psutil
import logging
from PIL import ImageTk,Image
from tkinter import messagebox


class main:
    #Creating a global variable
    img_name = '0'

    def __init__(self, root):
        self.root = root
        self.root.geometry("600x250")
        self.root.title(" Query Visualiser ")
        
        #To verify user's database password
        password = tk.StringVar()
        L1 = Label(self.root, text="Input password:")
        E1 = Entry(self.root, textvariable=password, show='*', bd =5)

        #Setting default database = TPC-H
        L = Label(self.root, text="If your database is TPC-H, you only need to enter your password")
        
        #To access the database and retrieve the data
        L2 = Label(self.root, text="Input your database: (e.g. TPC-H)")
        E2 = Entry(self.root, bd =5)
        
        #To access correct host
        L3 = Label(self.root, text="Input hostname: (e.g. localhost)")
        E3 = Entry(self.root, bd =5)
        
        #To retriver user's username
        L4 = Label(self.root, text="Input username: (e.g. postgres)")
        E4 = Entry(self.root, bd =5)
        
        #To retrieve data via correct port id
        L5 = Label(self.root, text="Input port id: (e.g. 5432)")
        E5 = Entry(self.root, bd =5)
        
        #Button to confirm submission
        #Calls on error_check() to verify inputted information
        pwd = Button(self.root, height = 2,
                 width = 15, 
                 text="confirm", 
                 command= lambda: error_check())
        
        #Button to exit application
        #Calls on root.destroy() funtion that destroys window and ends application
        exit_button = Button(self.root, height = 2,
                 width = 15, 
                 text="Exit", 
                 command=self.root.destroy)

        #Positioning Questions and inputs + confirm & exit button
        L1.place(relx=0.3, rely=0.1, anchor=CENTER)
        E1.place(relx=0.7, rely=0.1, anchor=CENTER)
        
        L.place(relx = 0.5, rely = 0.2, anchor = CENTER)

        L2.place(relx=0.3, rely=0.3, anchor=CENTER)
        E2.place(relx=0.7, rely=0.3, anchor=CENTER)
        
        L3.place(relx=0.3, rely=0.45, anchor=CENTER)
        E3.place(relx=0.7, rely=0.45, anchor=CENTER)
        
        L4.place(relx=0.3, rely=0.6, anchor=CENTER)
        E4.place(relx=0.7, rely=0.6, anchor=CENTER)
        
        L5.place(relx=0.3, rely=0.75, anchor=CENTER)
        E5.place(relx=0.7, rely=0.75, anchor=CENTER)
        
        pwd.place(relx=0.3, rely=0.9, anchor=CENTER)
        exit_button.place(relx=0.7, rely=0.9, anchor=CENTER)
        
        #Checking user's password, database, hostname and username to retrieve correct set of data
        def error_check():
            try:
                pwd = E1.get()
                if E3.get() == None:
                    hostname = E3.get()
                else:
                    hostname = 'localhost'
                if E4.get() == None:
                    username = E4.get()
                else:
                    username = 'postgres'
                if E5.get() == None:
                    port_id = E5.get()
                else:
                    port_id ="5432"
                if E2.get() == None:
                    database = E2.get()
                else:
                    database = 'TPC-H'

                #Calling the query visualiser    
                init_db(pwd, hostname, database, username, port_id)
            except:
                tk.messagebox.showerror('error', 'Invalid field for password, try again!')
    
        def init_db(pwd, hostname, database, username, port_id):
            #Creating a new window on top of the root windowS
            newWindow = Toplevel()
            self.newWindow = newWindow
            self.newWindow.geometry("750x1000")

            try:
                # Function restart_program(runner): to enter a new query
                def restart_program(runner):
                    """Restarts the current program, with file objects and descriptors cleanup"""
                    try:
                        p = psutil.Process(os.getpid())
                        for handler in p.get_open_files() + p.connections():
                            os.close(handler.fd)
                        runner.tear_down_db_connection()
                    except Exception as e:
                        logging.error(e)
                    
                    python = sys.executable
                    os.execl(python, python, *sys.argv)
                
                #Restarts the main application window, so user doesn't have to log in again
                def restart_window(runner, pwd):
                    newWindow.destroy()
                    init_db(pwd)
                
                #Destorys the window and ends application
                def exit(runner):
                    """Destroys the window and tear down connection"""
                    root.destroy
                    runner.tear_down_db_connection()

                q = QueryRunner(pwd)
                l = Label(text = "Input query").pack()

                #Where users can input their queries: yellow rectangle
                inputtxt = Text(self.newWindow, height = 20,
                                width = 60,
                                bg = "light yellow")
                inputtxt.pack()
                
                #Takes in the query, and calls on function Take_input() to process and outputs the query steps and plan
                query = Button(self.newWindow, height = 2,
                              width = 20, 
                              text="Show", 
                              command= lambda:Take_input())
                query.pack()

                #Closes program and restarts all over again
                restart_button = Button(self.newWindow, height = 2,
                                        width = 20,
                                        text="Change Database",
                                        command= lambda: restart_program(q))

                restart_button.pack()

                #Wipes the previous query and opens a new window for a new query
                restart_window_button = Button(self.newWindow, height = 2,
                                        width = 20,
                                        text="Next Query",
                                        command= lambda: restart_window(q, pwd))

                restart_window_button.pack()

                #When user's use is finished, he/she can simply close the GUI by clicking on the exit button
                # Calls on the exit functions    
                exit_button = Button(self.newWindow, height = 2,
                                    width = 20, 
                                    text="Exit",
                                    command= lambda: exit(q))
                exit_button.pack()

                #Whenre the query plan (i.e. the steps) are displayed in a sequential order: blue rectangle
                Output = Text(self.newWindow, height = 20, 
                              width = 120, 
                              bg = "light cyan")
                Output.pack()
                
                #Takes in query written by the user to generate the query plan and the graph (query image)
                def Take_input():
                    global img_name
                    qry = inputtxt.get("1.0", "end-1c")
                    
                    explain = q.explain(qry)

                    #Create the graph and saves it in a png format
                    #save_graph_file() function returns a string, name of the image, that is stored in the global variable img_name
                    img_name = explain.save_graph_file()

                    #Generate explanation/annotation for each step for the inputted query 
                    plan = explain.create_explanation(explain.root)
                    # generates steps
                    count = 0
                    output = " "
                    for i in plan:
                        count +=1
                        output+=f"Step {count}: {i} \n"

                    Output.insert(tk.END, output)

                #Reads and generate the query plan image in a window on top of the query visualiser    
                def open_query():
                    global img_name 
                    top = Toplevel()
                    top.title("Query Visualiser")
                    width_screen, height_screen = top.winfo_screenwidth(), top.winfo_screenheight()
                    top.geometry('%dx%d+0+0' % (int(width_screen/1.5),int(height_screen/1.5)))

                    #Define image 
                    bg = ImageTk.PhotoImage(file = img_name)

                    #Create a canvas
                    my_canvas = Canvas(top, width = int(width_screen/1.5), height = int(height_screen/1.5))
                    my_canvas.pack(fill="both", expand=True)
                        
                    #Set image in canvas
                    my_canvas.create_image(0,0, image =bg, anchor = "nw")

                    #To allow for dynamic resizing of the image in response to the change in window size
                    # i.e. change the size of the window, will cause the image size to change with it    
                    def resizer(e):                            
                        global bg1, resized_bg, new_bg
                        #open image
                        bg1 = Image.open(img_name)
                        #resize image
                        resized_bg = bg1.resize((e.width, e.height), Image.ANTIALIAS)
                        #Define image
                        new_bg = ImageTk.PhotoImage(resized_bg)
                        my_canvas.create_image(0,0, image = new_bg, anchor = "nw" )

                    top.bind('<Configure>', resizer)
                    top.mainloop()

                #Button to generate the query plan image on the main window
                query_plan_button = Button(self.newWindow, height = 2,
                                        width = 20,
                                        text="Generate Query Plan", 
                                        command=open_query,)
                query_plan_button.pack()
                
            except:
                tk.messagebox.showerror('error', 'Wrong password, try again!')
            
        

        self.root.mainloop()