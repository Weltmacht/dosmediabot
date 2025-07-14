from tkinter import *
from tkinter import ttk
import sqlite3
import time

class DOSBotUI:
    def get_env_data_as_dict(self, path: str) -> dict:
        try:
            with open(path, 'r') as f:
                return dict(tuple(line.replace('\n', '').split('=')) for line
                    in f.readlines() if not line.startswith('#'))
        except: 
            print("You need to include the .env file, John, with the APP_ID=<appid> and APP_SECRET=<secret>(don't show others this! its your bot!)")

    def __init__(self):
        self.ws = Tk()
        self.var1 = IntVar()
        self.setup_window()
        self.create_widgets()
        
    def setup_window(self):
        self.ws.title('DOSBot')
        self.ws.geometry('650x300')
        
    def create_widgets(self):
        # Main frame
        queue_frame = Frame(self.ws)
        queue_frame.pack()
        
        # Scrollbar
        queue_scroll = Scrollbar(queue_frame)
        queue_scroll.pack(side=RIGHT, fill=Y)
        
        # Treeview
        self.my_queue = ttk.Treeview(queue_frame, yscrollcommand=queue_scroll.set)
        self.my_queue.pack()
        queue_scroll.config(command=self.my_queue.yview)
        
        # Mouse click events
        self.my_queue.bind("<ButtonRelease-1>", self.onLeftClick)
        self.my_queue.bind("<Double-Button-1>", self.onDoubleClick)        
        self.my_queue.bind("<ButtonRelease-3>", self.onRightClick)

        # Configure columns
        self.my_queue['columns'] = ('id', 'name', 'link', 'method', 'time')
        self.my_queue.column("#0", width=0, stretch=YES)
        self.my_queue.column("id", anchor=CENTER, width=0)
        self.my_queue.column("name", anchor=CENTER, width=140)
        self.my_queue.column("link", anchor=W, width=300)
        self.my_queue.column("method", anchor=CENTER, width=50)
        self.my_queue.column("time", anchor=W, width=110)
        
        # Configure headings
        self.my_queue.heading("#0", text="", anchor=CENTER)
        self.my_queue.heading("id", text="Id", anchor=CENTER)
        self.my_queue.heading("name", text="Name", anchor=CENTER)
        self.my_queue.heading("link", text="Link", anchor=CENTER)
        self.my_queue.heading("method", text="Method", anchor=CENTER)
        self.my_queue.heading("time", text="Time", anchor=CENTER)
        
        bottom = Frame(self.ws)
        bottom.pack(side=BOTTOM, fill=BOTH, expand=True)

        # Buttons
        refresh = Button(self.ws, text="Refresh", command=self.read_queue)
        refresh.pack(in_=bottom, side=LEFT, padx=30)
        
        delete = Button(self.ws, text="Delete", command=self.delete_item)
        delete.pack(in_=bottom, side=LEFT)

        c1 = Checkbutton(self.ws, text='Always On Top', variable=self.var1, 
                        onvalue=1, offvalue=0, command=self.makeontop)
        c1.pack(in_=bottom, side=RIGHT, padx=25)

        self.read_queue()

    #Event handlers for table
    def onLeftClick(self, args):
        selected = self.my_queue.selection()
        if selected:
            item = self.my_queue.item(selected[0])
            url = item['values'][2]
            self.ws.clipboard_clear()
            self.ws.clipboard_append(url)
            #self.my_queue.item(selected, tags=('selected_row',))
            #self.my_queue.tag_configure('selected_row', background='yellow')

    #Event handlers for table
    def onRightClick(self, args):
        selected = self.my_queue.selection()
        if selected:
            self.my_queue.item(selected, tags=('selected_row',))
            self.my_queue.tag_configure('selected_row', background='white')

    def onDoubleClick(self, args):
        selected = self.my_queue.selection()
        if(selected and (self.get_env_data_as_dict('.env')["DBLCLK_DEL"] == "True" or self.get_env_data_as_dict('.env')["DBLCLK_DEL"] == "true")):
            item = self.my_queue.item(selected[0])
            url = item['values'][2]
            self.ws.clipboard_clear()
            self.ws.clipboard_append(url)
            self.delete_item()

    # Some buttons
    def delete_item(self):
        selected = self.my_queue.selection()
        if selected:
            item = self.my_queue.item(selected[0])
            item_id = item['values'][0]
            connection = sqlite3.connect('queue.db')
            cursor = connection.cursor()
            cursor.execute(f"""DELETE FROM queue WHERE rowid = {item_id}""")
            connection.commit()
            connection.close()
        self.read_queue()
            
    def makeontop(self):
        if self.var1.get() == 1:
            self.ws.attributes('-topmost', True)
        else:
            self.ws.attributes('-topmost', False)
            
    def read_queue(self):
        try:
            connection = sqlite3.connect('queue.db')
            cursor = connection.cursor()
            cursor.execute("SELECT rowid, username, link, method, time FROM queue ORDER BY rowid ASC")
            rows = cursor.fetchall()
            connection.close()
            
            self.my_queue.delete(*self.my_queue.get_children())

            for row in rows:
                mklist = list(row)
                mklist[4] = time.strftime("%I:%M:%S %p", time.localtime(row[4]))
                self.my_queue.insert(parent='', index='end', text='', values=mklist)
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            
    def run(self):
        self.ws.mainloop()

def main():
    app = DOSBotUI()
    app.run()

if __name__ == "__main__":
    main()