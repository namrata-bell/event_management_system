import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import mysql.connector
from datetime import datetime

class CustomerPortal:
    def __init__(self, root):
        self.root = root
        self.root.title("Event Management System - Customer Portal")
        self.root.geometry("900x700")
        
        # Color scheme
        self.bg_color = "#f0f4f8"
        self.primary_color = "#4a90e2"
        self.secondary_color = "#50c878"
        self.accent_color = "#ff6b6b"
        self.dark_color = "#2c3e50"
        self.light_color = "#ffffff"
        
        self.root.configure(bg=self.bg_color)
        
        # Database connection
        self.conn = None
        self.cursor = None
        self.current_user_id = None
        self.current_user_type = None
        self.current_user_name = None
        
        # Configure styles
        self.setup_styles()
        
        # Setup UI
        self.setup_connection_frame()
        self.setup_main_menu()
        
    def setup_styles(self):
        """Configure ttk styles with colors"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure frames
        style.configure("TFrame", background=self.bg_color)
        style.configure("TLabelFrame", background=self.bg_color, foreground=self.dark_color, 
                       borderwidth=2, relief="solid")
        style.configure("TLabelFrame.Label", background=self.bg_color, foreground=self.dark_color, 
                       font=("Arial", 10, "bold"))
        
        # Configure labels
        style.configure("TLabel", background=self.bg_color, foreground=self.dark_color, 
                       font=("Arial", 10))
        
        # Configure buttons
        style.configure("TButton", background=self.primary_color, foreground=self.light_color,
                       font=("Arial", 10, "bold"), borderwidth=0, focuscolor='none')
        style.map("TButton",
                 background=[('active', '#3a7bc8'), ('pressed', '#2c5aa0')])
        
        # Configure entry
        style.configure("TEntry", fieldbackground=self.light_color, foreground=self.dark_color,
                       borderwidth=2)
        
        # Configure combobox
        style.configure("TCombobox", fieldbackground=self.light_color, background=self.light_color,
                       foreground=self.dark_color, borderwidth=2)
        
    def setup_connection_frame(self):
        """Database connection frame"""
        conn_frame = ttk.LabelFrame(self.root, text="Database Connection", padding=10)
        conn_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(conn_frame, text="Host:").grid(row=0, column=0, padx=5)
        self.host_entry = ttk.Entry(conn_frame, width=15)
        self.host_entry.insert(0, "localhost")
        self.host_entry.grid(row=0, column=1, padx=5)
        
        ttk.Label(conn_frame, text="User:").grid(row=0, column=2, padx=5)
        self.user_entry = ttk.Entry(conn_frame, width=15)
        self.user_entry.insert(0, "root")
        self.user_entry.grid(row=0, column=3, padx=5)
        
        ttk.Label(conn_frame, text="Password:").grid(row=0, column=4, padx=5)
        self.pass_entry = ttk.Entry(conn_frame, show="*", width=15)
        self.pass_entry.grid(row=0, column=5, padx=5)
        
        ttk.Label(conn_frame, text="Database:").grid(row=0, column=6, padx=5)
        self.db_entry = ttk.Entry(conn_frame, width=20)
        self.db_entry.insert(0, "evm")
        self.db_entry.grid(row=0, column=7, padx=5)
        
        self.connect_btn = ttk.Button(conn_frame, text="Connect", command=self.connect_db)
        self.connect_btn.grid(row=0, column=8, padx=10)
        
        self.status_label = ttk.Label(conn_frame, text="Not Connected", foreground="#e74c3c")
        self.status_label.grid(row=0, column=9, padx=5)
        
    def connect_db(self):
        """Connect to MySQL database"""
        try:
            self.conn = mysql.connector.connect(
                host=self.host_entry.get(),
                user=self.user_entry.get(),
                password=self.pass_entry.get(),
                database=self.db_entry.get()
            )
            self.cursor = self.conn.cursor(dictionary=True)
            self.status_label.config(text="Connected ✓", foreground=self.secondary_color)
            messagebox.showinfo("Success", "Connected to database successfully!")
        except Exception as e:
            messagebox.showerror("Connection Error", str(e))
            self.status_label.config(text="Connection Failed", foreground=self.accent_color)
    
    def setup_main_menu(self):
        """Main menu frame"""
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Welcome label
        welcome_label = tk.Label(self.main_frame, 
                                 text="Welcome to Event Management Portal", 
                                 font=("Arial", 22, "bold"),
                                 bg=self.bg_color,
                                 fg=self.primary_color)
        welcome_label.pack(pady=30)
        
        # User status
        self.user_status_label = tk.Label(self.main_frame, 
                                          text="Not logged in", 
                                          font=("Arial", 12),
                                          bg=self.bg_color,
                                          fg="#7f8c8d")
        self.user_status_label.pack(pady=10)
        
        # Registration options
        reg_frame = ttk.LabelFrame(self.main_frame, text="Register or Login", padding=20)
        reg_frame.pack(pady=20, fill="x")
        
        reg_label = tk.Label(reg_frame, text="Please click on the button to register:", 
                            font=("Arial", 12),
                            bg=self.bg_color,
                            fg=self.dark_color)
        reg_label.pack(pady=10)
        
        btn_frame = ttk.Frame(reg_frame)
        btn_frame.pack(pady=10)
        
        register_btn = tk.Button(btn_frame, text="Register as Attendee", 
                  command=self.show_attendee_registration,
                  width=25,
                  bg=self.secondary_color,
                  fg=self.light_color,
                  font=("Arial", 11, "bold"),
                  relief="flat",
                  cursor="hand2",
                  activebackground="#3db864",
                  activeforeground=self.light_color)
        register_btn.pack(side="left", padx=10)
        
        
        # Browse events
        browse_frame = ttk.Frame(self.main_frame)
        browse_frame.pack(pady=20)
        
        browse_btn = tk.Button(browse_frame, text="Browse Events", 
                  command=self.show_events_browser,
                  width=40,
                  bg=self.primary_color,
                  fg=self.light_color,
                  font=("Arial", 12, "bold"),
                  relief="flat",
                  cursor="hand2",
                  activebackground="#3a7bc8",
                  activeforeground=self.light_color,
                  pady=10)
        browse_btn.pack(pady=10)
        
        # Logout button (initially hidden)
        self.logout_btn = tk.Button(self.main_frame, text="Logout", 
                                    command=self.logout,
                                    width=20,
                                    bg=self.accent_color,
                                    fg=self.light_color,
                                    font=("Arial", 10, "bold"),
                                    relief="flat",
                                    cursor="hand2",
                                    activebackground="#e55555",
                                    activeforeground=self.light_color)
        
    def show_attendee_registration(self):
        """Show attendee registration form"""
        if not self.conn:
            messagebox.showerror("Error", "Please connect to database first!")
            return
        
        reg_window = tk.Toplevel(self.root)
        reg_window.title("Attendee Registration")
        reg_window.geometry("500x500")
        reg_window.configure(bg=self.bg_color)
        
        form_frame = ttk.Frame(reg_window, padding=20)
        form_frame.pack(fill="both", expand=True)
        
        title_label = tk.Label(form_frame, text="Attendee Registration", 
                              font=("Arial", 18, "bold"),
                              bg=self.bg_color,
                              fg=self.primary_color)
        title_label.grid(row=0, column=0, columnspan=2, pady=20)
        
        fields = [
            ("Full Name: *", "name"),
            ("Phone Number: *", "phone"),
            ("Email: *", "email"),
            ("Gender:", "gender"),
            ("Age:", "age")
        ]
        
        entries = {}
        for i, (label, key) in enumerate(fields, start=1):
            ttk.Label(form_frame, text=label).grid(row=i, column=0, sticky="w", pady=10, padx=5)
            if key == "gender":
                entries[key] = ttk.Combobox(form_frame, width=30, values=["M", "F", "O"])
            else:
                entries[key] = ttk.Entry(form_frame, width=32)
            entries[key].grid(row=i, column=1, pady=10, padx=5)
        
        def register_attendee():
            try:
                query = """INSERT INTO Attendee (name, phone_no, email, gender, age)
                          VALUES (%s, %s, %s, %s, %s)"""
                values = (
                    entries['name'].get(),
                    entries['phone'].get(),
                    entries['email'].get(),
                    entries['gender'].get() if entries['gender'].get() else None,
                    int(entries['age'].get()) if entries['age'].get() else None
                )
                self.cursor.execute(query, values)
                self.conn.commit()
                
                # Get the new attendee ID
                self.current_user_id = self.cursor.lastrowid
                self.current_user_type = "Attendee"
                self.current_user_name = entries['name'].get()
                
                messagebox.showinfo("Success", 
                                  f"Registration successful!\nYour Attendee ID is: {self.current_user_id}")
                self.update_user_status()
                reg_window.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Registration failed: {str(e)}")
        
        register_btn = tk.Button(form_frame, text="Register", command=register_attendee,
                  width=20,
                  bg=self.secondary_color,
                  fg=self.light_color,
                  font=("Arial", 11, "bold"),
                  relief="flat",
                  cursor="hand2")
        register_btn.grid(row=len(fields)+1, column=0, columnspan=2, pady=20)
        
        req_label = tk.Label(form_frame, text="* Required fields", 
                            bg=self.bg_color,
                            fg="#7f8c8d")
        req_label.grid(row=len(fields)+2, column=0, columnspan=2)
    
    def show_events_browser(self):
        """Show events browser and booking interface"""
        if not self.conn:
            messagebox.showerror("Error", "Please connect to database first!")
            return
        
        browser_window = tk.Toplevel(self.root)
        browser_window.title("Browse Events")
        browser_window.geometry("1000x600")
        browser_window.configure(bg=self.bg_color)
        
        # Title
        title_label = tk.Label(browser_window, text="Available Events", 
                              font=("Arial", 18, "bold"),
                              bg=self.bg_color,
                              fg=self.primary_color)
        title_label.pack(pady=10)
        
        # Events list
        list_frame = ttk.Frame(browser_window)
        list_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        columns = ("ID", "Name", "Date", "Time", "Venue", "Status")
        events_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)
        
        # Configure treeview colors
        style = ttk.Style()
        style.configure("Treeview", background=self.light_color, foreground=self.dark_color,
                       fieldbackground=self.light_color, font=("Arial", 9))
        style.configure("Treeview.Heading", background=self.primary_color, foreground=self.light_color,
                       font=("Arial", 10, "bold"))
        style.map("Treeview", background=[('selected', self.primary_color)])
        
        for col in columns:
            events_tree.heading(col, text=col)
            events_tree.column(col, width=150)
        
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=events_tree.yview)
        events_tree.configure(yscrollcommand=scrollbar.set)
        
        events_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Load events
        try:
            query = """
                SELECT e.eventID, e.name, e.date, e.start_time, v.name as venue_name, e.status
                FROM Events e
                JOIN Venue v ON e.venueID = v.venueID
                WHERE e.status = 'Planned' AND e.date >= CURDATE()
                ORDER BY e.date
            """
            self.cursor.execute(query)
            events = self.cursor.fetchall()
            
            for event in events:
                events_tree.insert("", "end", values=(
                    event['eventID'],
                    event['name'],
                    event['date'],
                    event['start_time'],
                    event['venue_name'],
                    event['status']
                ))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load events: {str(e)}")
        
        # Buttons frame
        btn_frame = ttk.Frame(browser_window)
        btn_frame.pack(pady=10)
        
        def view_tickets():
            selection = events_tree.selection()
            if not selection:
                messagebox.showwarning("Warning", "Please select an event first!")
                return
            
            event_id = events_tree.item(selection[0])['values'][0]
            self.show_tickets_for_event(event_id)
        
        def view_event_details():
            selection = events_tree.selection()
            if not selection:
                messagebox.showwarning("Warning", "Please select an event first!")
                return
            
            event_id = events_tree.item(selection[0])['values'][0]
            self.show_event_details(event_id)
        
        details_btn = tk.Button(btn_frame, text="View Event Details", 
                  command=view_event_details, width=25,
                  bg="#9b59b6", fg=self.light_color,
                  font=("Arial", 10, "bold"), relief="flat", cursor="hand2")
        details_btn.pack(side="left", padx=10)
        
        tickets_btn = tk.Button(btn_frame, text="View Available Tickets", 
                  command=view_tickets, width=25,
                  bg=self.secondary_color, fg=self.light_color,
                  font=("Arial", 10, "bold"), relief="flat", cursor="hand2")
        tickets_btn.pack(side="left", padx=10)
    
    def show_event_details(self, event_id):
        """Show detailed event information"""
        details_window = tk.Toplevel(self.root)
        details_window.title("Event Details")
        details_window.geometry("700x500")
        details_window.configure(bg=self.bg_color)
        
        text_area = scrolledtext.ScrolledText(details_window, wrap=tk.WORD, 
                                             font=("Arial", 10), padx=20, pady=20,
                                             bg=self.light_color, fg=self.dark_color)
        text_area.pack(fill="both", expand=True)
        
        try:
            # Get event info
            query = """
                SELECT e.*, v.name as venue_name, v.address, v.capacity, v.type as venue_type
                FROM Events e
                JOIN Venue v ON e.venueID = v.venueID
                WHERE e.eventID = %s
            """
            self.cursor.execute(query, (event_id,))
            event = self.cursor.fetchone()
            
            text_area.insert(tk.END, f"{'='*60}\n")
            text_area.insert(tk.END, f"{event['name']}\n")
            text_area.insert(tk.END, f"{'='*60}\n\n")
            
            text_area.insert(tk.END, f"Event ID: {event['eventID']}\n")
            text_area.insert(tk.END, f"Date: {event['date']}\n")
            text_area.insert(tk.END, f"Time: {event['start_time']} - {event['end_time']}\n")
            text_area.insert(tk.END, f"Status: {event['status']}\n")
            text_area.insert(tk.END, f"Budget: ₹{event['budget']:,.2f}\n\n")
            
            text_area.insert(tk.END, f"Venue Information:\n")
            text_area.insert(tk.END, f"  Name: {event['venue_name']}\n")
            text_area.insert(tk.END, f"  Type: {event['venue_type']}\n")
            text_area.insert(tk.END, f"  Address: {event['address']}\n")
            text_area.insert(tk.END, f"  Capacity: {event['capacity']}\n\n")
            
            # Get artists
            self.cursor.execute("""
                SELECT a.name, a.genre, p.noOfSongs
                FROM Artist a
                JOIN performs p ON a.artistID = p.artistID
                WHERE p.eventID = %s
            """, (event_id,))
            artists = self.cursor.fetchall()
            
            if artists:
                text_area.insert(tk.END, f"Performing Artists:\n")
                for artist in artists:
                    text_area.insert(tk.END, 
                                   f"  • {artist['name']} ({artist['genre']}) - {artist['noOfSongs']} songs\n")
                text_area.insert(tk.END, "\n")
            
            # Get ticket info
            self.cursor.execute("""
                SELECT type, COUNT(*) as total, 
                       SUM(CASE WHEN status = 'AVAILABLE' THEN 1 ELSE 0 END) as available,
                       MIN(price) as min_price, MAX(price) as max_price
                FROM Ticket
                WHERE eventID = %s
                GROUP BY type
            """, (event_id,))
            tickets = self.cursor.fetchall()
            
            if tickets:
                text_area.insert(tk.END, f"Ticket Information:\n")
                for ticket in tickets:
                    text_area.insert(tk.END, 
                                   f"  • {ticket['type']}: {ticket['available']}/{ticket['total']} available "
                                   f"(₹{ticket['min_price']}-₹{ticket['max_price']})\n")
            
            text_area.config(state='disabled')
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load event details: {str(e)}")
    
    def show_tickets_for_event(self, event_id):
        """Show available tickets for an event"""
        if not self.current_user_id or self.current_user_type != "Attendee":
            messagebox.showwarning("Login Required", 
                                 "Please register/login as an Attendee to book tickets!")
            return
        
        tickets_window = tk.Toplevel(self.root)
        tickets_window.title("Available Tickets")
        tickets_window.geometry("800x500")
        tickets_window.configure(bg=self.bg_color)
        
        # Title
        title_label = tk.Label(tickets_window, text="Select a Ticket to Book", 
                              font=("Arial", 16, "bold"),
                              bg=self.bg_color,
                              fg=self.primary_color)
        title_label.pack(pady=10)
        
        # Tickets list
        list_frame = ttk.Frame(tickets_window)
        list_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        columns = ("Ticket ID", "Type", "Seat", "Price", "Status")
        tickets_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            tickets_tree.heading(col, text=col)
            tickets_tree.column(col, width=150)
        
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=tickets_tree.yview)
        tickets_tree.configure(yscrollcommand=scrollbar.set)
        
        tickets_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Load tickets
        try:
            query = """
                SELECT ticketID, type, seatNo, price, status
                FROM Ticket
                WHERE eventID = %s AND status = 'AVAILABLE'
                ORDER BY type, seatNo
            """
            self.cursor.execute(query, (event_id,))
            tickets = self.cursor.fetchall()
            
            for ticket in tickets:
                tickets_tree.insert("", "end", values=(
                    ticket['ticketID'],
                    ticket['type'],
                    ticket['seatNo'],
                    f"₹{ticket['price']}",
                    ticket['status']
                ))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load tickets: {str(e)}")
        
        # Book button
        def book_ticket():
            selection = tickets_tree.selection()
            if not selection:
                messagebox.showwarning("Warning", "Please select a ticket!")
                return
            
            ticket_id = tickets_tree.item(selection[0])['values'][0]
            
            if messagebox.askyesno("Confirm Booking", 
                                  "Do you want to book this ticket?"):
                try:
                    # Insert into purchases table (trigger will update ticket status)
                    query = "INSERT INTO purchases (attendeeID, ticketID) VALUES (%s, %s)"
                    self.cursor.execute(query, (self.current_user_id, ticket_id))
                    self.conn.commit()
                    
                    # Also add to attends table if not already there
                    try:
                        query2 = "INSERT INTO attends (attendeeID, eventID) VALUES (%s, %s)"
                        self.cursor.execute(query2, (self.current_user_id, event_id))
                        self.conn.commit()
                    except:
                        pass  # Already attending
                    
                    messagebox.showinfo("Success", 
                                      "Ticket booked successfully!\n"
                                      "Confirmation has been recorded in the system.")
                    tickets_window.destroy()
                except Exception as e:
                    messagebox.showerror("Error", f"Booking failed: {str(e)}")
        
        book_btn = tk.Button(tickets_window, text="Book Selected Ticket", 
                  command=book_ticket, width=30,
                  bg=self.secondary_color, fg=self.light_color,
                  font=("Arial", 11, "bold"), relief="flat", cursor="hand2",
                  pady=8)
        book_btn.pack(pady=10)
    
    def update_user_status(self):
        """Update user status label"""
        if self.current_user_id:
            self.user_status_label.config(
                text=f"Logged in as: {self.current_user_name} ({self.current_user_type} ID: {self.current_user_id})",
                fg=self.secondary_color
            )
            self.logout_btn.pack(pady=10)
        else:
            self.user_status_label.config(text="Not logged in", fg="#7f8c8d")
            self.logout_btn.pack_forget()
    
    def logout(self):
        """Logout current user"""
        self.current_user_id = None
        self.current_user_type = None
        self.current_user_name = None
        self.update_user_status()
        messagebox.showinfo("Logged Out", "You have been logged out successfully!")
    
    def __del__(self):
        if self.conn:
            self.cursor.close()
            self.conn.close()


if __name__ == "__main__":
    root = tk.Tk()
    app = CustomerPortal(root)
    root.mainloop()