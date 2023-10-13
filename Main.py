import json
import tkinter as tk
from tkinter import ttk, filedialog
from tkinter.ttk import Frame, Label, Entry, Button
import socket
from tkinter import messagebox, simpledialog
from ds_messenger import *
from datetime import datetime


class AddUserError(Exception):
    pass


class DMSendError(Exception):
    pass


class UserLogin(Frame):
    """Allows a user to login to an existing account or create a new one"""

    # Code based off Alan's SimpleDialog Class at https://stackoverflow.com/questions/50573260/simpledialog-simpledialog-in-python-with-2-inputsh
    def __init__(self):
        super().__init__()
        # Creating class attributes that will be returned to the function call
        self.username, self.password = '', ''
        self.input_box()

    def input_box(self):
        """Populates frame attributes and recieves login details from user input."""
        self.master.title("New / Existing User Login")
        self.pack(fill=tk.BOTH, expand=True)

        frame1 = Frame(self)
        frame1.pack(fill=tk.X)

        # Separate labels and frames for username and password as both attributes are required to login
        lbl1 = Label(frame1, text="Username", width=10)
        lbl1.pack(side=tk.LEFT, padx=5, pady=10)

        self.entry1 = Entry(frame1, textvariable=self.username)
        self.entry1.pack(fill=tk.X, padx=5, expand=True)

        frame2 = Frame(self)
        frame2.pack(fill=tk.X)

        # Separate labels and frames continued
        lbl2 = Label(frame2, text="Password", width=10)
        lbl2.pack(side=tk.LEFT, padx=5, pady=10)

        self.entry2 = Entry(frame2)
        self.entry2.pack(fill=tk.X, padx=5, expand=True)

        frame3 = Frame(self)
        frame3.pack(fill=tk.X)

        # When the button is pushed user input populates the class attributes
        btn = Button(frame3, text="Let me in!", command=self.populate_vars)
        btn.pack(padx=5, pady=10)

    def populate_vars(self):
        """Populates username and password attributes based on user input and closes the frame."""
        self.username = self.entry1.get()
        self.password = self.entry2.get()
        self.quit()


class Body(tk.Frame):
    """A subclass of tk.Frame responsible for drawing all of the widgets in the body portion of the root frame."""

    def __init__(self, root, select_callback=None):
        tk.Frame.__init__(self, root)
        self.root = root
        self._select_callback = select_callback
        # A list for recipients allows individual recipients to be appended from a loop
        self.recipients = []
        # Saving the currently selected node and recipient allows the correspending user's messages to be printed to the Frame
        self.selected_node = None
        self.current_recipient = None

        # After all initialization is complete the _draw method packs the widgets into the Body instance
        self._draw()

    def node_select(self, event):
        """Updates the dm_displayer with a user's chat history when the corresponding node in recipient_tree is selected."""
        # Selections are not 0-based, one is subtracted
        index = int(self.recipients_tree.selection()[0]) - 1
        # Each node's index corresponds to a DirectMessage obj's index, indexing the same value for both displays the correct user's messages
        self.selected_node = index
        get_recipients = DirectMessenger(username=username, password=password, port=3021)
        get_recipients = get_recipients.retrieve_all()

        all_recieved_messages = ""
        list_temp, i = [], 0
        try:
            if index in range(len(get_recipients)):
                # Iterates through each message and displays said messages in its corresponding recipient node
                for message in (get_recipients[index].message):
                    # Saves currently selected recipient to the class
                    self.current_recipient = (get_recipients[index].recipient)
                    # Combines a message, its correspending timestamp, and a newline into a single string and appends it to a list
                    tempo_str = (str(datetime.fromtimestamp(float(get_recipients[index].timestamp[i]))) + ': ' +
                                 get_recipients[index].message[i])
                    tempo = str(tempo_str + '\n')
                    all_recieved_messages = all_recieved_messages + tempo
                    list_temp.append(tempo)
                    i += 1
                # Sets dm_displayer's text to the message history of a selected recipient w/ timestamps
                self.set_text_entry(all_recieved_messages)
            else:
                self.current_recipient = self.recipients_tree.item(self.recipients_tree.selection()[0])["text"]
                self.set_text_entry("")
        except Exception as exc:
            print("There was an error selecting this user:\n" + exc)

    def get_text_entry(self) -> str:
        """Returns the text that is currently displayed in the dm_displayer widget."""
        return self.dm_displayer.get('1.0', 'end').rstrip()

    def set_text_entry(self, text):
        """Sets the text to be displayed in the dm_displayer widget."""
        self.dm_displayer.delete(0.0, 'end')
        self.dm_displayer.insert(0.0, text)

    def get_editor_entry(self) -> str:
        """Returns the text that is currently displayed in the dm_editor widget."""
        return self.dm_editor.get('1.0', 'end').rstrip()

    def set_editor_entry(self, text):
        """Sets the text to be displayed in the dm_editor widget."""
        self.dm_editor.delete(0.0, 'end')
        self.dm_editor.insert(0.0, text)

    def set_recipients(self, recipients: list):
        """Inserts recipients into the treeview widget."""
        for temp_id, appended_recipient in enumerate(recipients):
            self._insert_recipient_tree(temp_id + 1, appended_recipient)

    def insert_recipient(self, recipient_name):
        """Inserts a single recipient to the recipient_tree widget."""
        self.recipients.append(recipient_name)
        self._insert_recipient_tree(len((self.recipients_tree.get_children())) + 1, recipient_name)

    def reset_ui(self):
        """Resets all UI widgets to their default state."""
        self.set_text_entry("")
        self.recipients = []
        for item in self.recipients_tree.get_children():
            self.recipients_tree.delete(item)

    def _insert_recipient_tree(self, id, recipient):
        """Inserts a recipient into the recipient_tree widget."""
        if len(recipient) > 25:
            recipient = recipient[:24] + "..."
        self.recipients_tree.insert('', id, id, text=recipient)

    def _draw(self):
        """Called once upon initialization to add widgets to the frame."""
        frame = tk.Frame(master=self, width=250)
        frame.pack(fill=tk.BOTH, side=tk.LEFT)

        self.recipients_tree = ttk.Treeview(frame)
        self.recipients_tree.bind("<<TreeviewSelect>>", self.node_select)
        self.recipients_tree.pack(fill=tk.BOTH, side=tk.TOP, expand=True, padx=5, pady=5)

        entry_frame = tk.Frame(master=self, bg="", height=15)
        entry_frame.pack(fill=tk.BOTH, side=tk.TOP, expand=False)

        editor_frame = tk.Frame(master=entry_frame, bg="red")
        editor_frame.pack(fill=tk.BOTH, side=tk.LEFT, expand=True)

        scroll_frame = tk.Frame(master=entry_frame, bg="blue", width=10)
        scroll_frame.pack(fill=tk.BOTH, side=tk.LEFT, expand=False)

        self.dm_displayer = tk.Text(editor_frame, width=0)
        self.dm_displayer.pack(fill=tk.BOTH, side=tk.TOP, expand=True, padx=0, pady=0)

        # New text box for messages to be sent in + users to be added
        self.dm_editor = tk.Text(master=self, width=0, height=10)
        self.dm_editor.pack(fill=tk.BOTH, side=tk.BOTTOM, expand=True, padx=0, pady=0)

        dm_displayer_scrollbar = tk.Scrollbar(master=scroll_frame, command=self.dm_displayer.yview)
        self.dm_displayer['yscrollcommand'] = dm_displayer_scrollbar.set
        dm_displayer_scrollbar.pack(fill=tk.BOTH, side=tk.LEFT, expand=False, padx=0, pady=0)


class Footer(tk.Frame):
    """
    A subclass of tk.Frame responsible for drawing all of the widgets in the footer portion of the root frame.
    """

    def __init__(self, root):
        tk.Frame.__init__(self, root)
        self.root = root


class MainApp(tk.Frame):
    """
    A subclass of tk.Frame that is responsible for drawing all of the widgets in the main portion of the root frame.
    """

    def __init__(self, root):
        tk.Frame.__init__(self, root)
        self.root = root
        self._draw()
        # Populates the recipient treeview with recipients upon program initialization
        self.load_recipients()

    def close(self):
        """Closes the program when the 'Close' menu item is clicked."""
        self.root.destroy()

    def load_recipients(self):
        """Populates / updates the recipient treeview with recipients."""
        self.body.reset_ui()
        get_recipients = DirectMessenger(username=username, password=password, port=3021)
        # Only populates the treeview with recipients who have already sent a message to the user
        try:
            get_recipients = get_recipients.retrieve_all()
            list_temp = []
            for obj in get_recipients:
                list_temp.append(obj.recipient)
            # Passing a list of DirectMessage object recipients into set_recipients
            self.body.set_recipients(list_temp)
        except ConnectError as exc:
            print("There was an error connecting to the server.")
            print(exc)
        except RetrievalError as exc:
            print("There was an error retrieving direct messages.")
            print(exc)

    def sending_a_message(self):
        """Sends a message to a recipient through the menu."""
        send_obj = DirectMessenger(username=username, password=password)
        # Retrieves message to be sent from dm_editor
        text = self.body.get_editor_entry()
        try:
            did_it_work = send_obj.send(text, self.body.current_recipient)

            # Server message tells the program whether or not the message sent successfully, if not, did_it_work is False
            if did_it_work is not True:
                raise DMSendError("An error occurred while trying to send this message")
        except DMSendError as exc:
            print(exc)
        except ConnectError as exc:
            print("There was an error connecting to the server.")
            print(exc)
        except Exception as exc:
            print('Something went incredibly horribly wrong!')
            print(exc)
        # Resets / empties dm_editor's textbox
        self.body.set_editor_entry('')

    def add_user(self):
        """Adds a user to the recipient tree through the menu."""
        try:
            new_user = self.body.get_editor_entry()
            # Resets / empties dm_editor's textbox
            self.body.set_editor_entry('')
            self.body.insert_recipient(new_user)
        except Exception as exc:
            print("There was an error adding this user:")
            print(exc)

    def _draw(self):
        """Called only once upon initialization to add widgets to root frame."""
        menu_bar = tk.Menu(self.root)
        self.root['menu'] = menu_bar
        menu_file = tk.Menu(menu_bar)
        menu_bar.add_cascade(menu=menu_file, label='File')
        # All custom commands in the menu, and call a function whenever clicked
        menu_file.add_command(label='Refresh', command=self.load_recipients)
        menu_file.add_command(label='Send', command=self.sending_a_message)
        menu_file.add_command(label='Add user', command=self.add_user)
        menu_file.add_command(label='Close', command=self.close)

        self.body = Body(self.root)
        self.body.pack(fill=tk.BOTH, side=tk.TOP, expand=True)
        self.footer = Footer(self.root)
        self.footer.pack(fill=tk.BOTH, side=tk.BOTTOM)


def populate_user_attributes():
    """Populates username and password with arguments given by user."""
    user_root = tk.Tk()
    user_root.geometry("300x150")
    login_obj = UserLogin()
    user_root.mainloop()
    # Returning list so that multiple attributes can be returned
    user_input = [login_obj.username, login_obj.password]
    user_root.destroy()
    return user_input


if __name__ == "__main__":
    user_attributes = populate_user_attributes()
    username, password = user_attributes[0], user_attributes[1]

    main = tk.Tk()
    main.title("JAM Direct Messenger")
    main.geometry("720x480")
    main.option_add('*tearOff', False)

    # Initialize the MainApp class
    MainApp(main)

    # Update ensures that we get an accurate width and height reading based on the types of widgets used
    main.update()
    main.minsize(main.winfo_width(), main.winfo_height())
    main.mainloop()