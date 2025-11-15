import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import mysql.connector
from datetime import datetime, date

class EventManagementAdminGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Event Management System - Admin Dashboard")
        self.root.geometry("1600x900")
        
        # Color scheme
        self.bg_color = "#ecf0f1"
        self.primary_color = "#3498db"
        self.secondary_color = "#2ecc71"
        self.accent_color = "#e74c3c"
        self.warning_color = "#f39c12"
        self.dark_color = "#2c3e50"
        self.light_color = "#ffffff"
        self.purple_color = "#9b59b6"
        self.teal_color = "#1abc9c"
        
        self.root.configure(bg=self.bg_color)
        
        # Database connection
        self.conn = None
        self.cursor = None
        
        # Configure styles
        self.setup_styles()
        
        # Setup UI
        self.setup_connection_frame()
        self.setup_main_interface()
        
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
                       font=("Arial", 9, "bold"), borderwidth=0, focuscolor='none')
        style.map("TButton",
                 background=[('active', '#2980b9'), ('pressed', '#1f6ba3')])
        
        # Configure entry
        style.configure("TEntry", fieldbackground=self.light_color, foreground=self.dark_color,
                       borderwidth=2)
        
        # Configure combobox
        style.configure("TCombobox", fieldbackground=self.light_color, background=self.light_color,
                       foreground=self.dark_color, borderwidth=2)
        
        # Configure notebook (tabs)
        style.configure("TNotebook", background=self.bg_color, borderwidth=0)
        style.configure("TNotebook.Tab", background="#bdc3c7", foreground=self.dark_color,
                       padding=[20, 10], font=("Arial", 10, "bold"))
        style.map("TNotebook.Tab",
                 background=[('selected', self.primary_color)],
                 foreground=[('selected', self.light_color)])
        
        # Configure treeview
        style.configure("Treeview", background=self.light_color, foreground=self.dark_color,
                       fieldbackground=self.light_color, font=("Arial", 9))
        style.configure("Treeview.Heading", background=self.primary_color, foreground=self.light_color,
                       font=("Arial", 9, "bold"), relief="flat")
        style.map("Treeview", background=[('selected', self.primary_color)])
        
    def setup_connection_frame(self):
        """Database connection frame"""
        conn_frame = ttk.LabelFrame(self.root, text="🔌 Database Connection", padding=10)
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
        
        self.connect_btn = tk.Button(conn_frame, text="Connect", command=self.connect_db,
                                     bg=self.secondary_color, fg=self.light_color,
                                     font=("Arial", 9, "bold"), relief="flat", cursor="hand2",
                                     padx=15)
        self.connect_btn.grid(row=0, column=8, padx=10)
        
        self.status_label = ttk.Label(conn_frame, text="❌ Not Connected", foreground=self.accent_color,
                                      font=("Arial", 10, "bold"))
        self.status_label.grid(row=0, column=9, padx=5)
        
    def setup_main_interface(self):
        """Main tabbed interface"""
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Create tabs
        self.create_dashboard_tab()
        self.create_events_tab()
        self.create_venues_tab()
        self.create_artists_tab()
        self.create_sponsors_tab()
        self.create_staff_tab()
        self.create_assignments_tab()
        self.create_reports_tab()
        self.create_analytics_tab()
        
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
            self.status_label.config(text="✓ Connected", foreground=self.secondary_color)
            messagebox.showinfo("Success", "Connected to database successfully!")
            self.load_dashboard_data()
        except Exception as e:
            messagebox.showerror("Connection Error", str(e))
            self.status_label.config(text="❌ Connection Failed", foreground=self.accent_color)
    
    def create_dashboard_tab(self):
        """Dashboard overview tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="📊 Dashboard")
        
        # Stats frame
        stats_frame = ttk.LabelFrame(tab, text="📈 System Overview", padding=20)
        stats_frame.pack(fill="x", padx=10, pady=10)
        
        self.dashboard_labels = {}
        stats = [
            ("Total Events", "events", self.primary_color),
            ("Active Events", "active_events", self.secondary_color),
            ("Total Venues", "venues", self.purple_color),
            ("Total Artists", "artists", self.warning_color),
            ("Total Sponsors", "sponsors", self.teal_color),
            ("Total Staff", "staff", "#e67e22")
        ]
        
        for i, (label, key, color) in enumerate(stats):
            frame = tk.Frame(stats_frame, bg=color, relief="raised", bd=2)
            frame.grid(row=i//3, column=i%3, padx=15, pady=15, sticky="ew")
            
            tk.Label(frame, text=label, font=("Arial", 11, "bold"), 
                    bg=color, fg=self.light_color, pady=5).pack()
            self.dashboard_labels[key] = tk.Label(frame, text="0", font=("Arial", 24, "bold"),
                                                  bg=color, fg=self.light_color, pady=5)
            self.dashboard_labels[key].pack()
        
        # Recent events
        recent_frame = ttk.LabelFrame(tab, text="📅 Upcoming Events", padding=10)
        recent_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        columns = ("ID", "Event", "Date", "Venue", "Status")
        self.dashboard_tree = ttk.Treeview(recent_frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.dashboard_tree.heading(col, text=col)
            self.dashboard_tree.column(col, width=150)
        
        scrollbar = ttk.Scrollbar(recent_frame, orient="vertical", command=self.dashboard_tree.yview)
        self.dashboard_tree.configure(yscrollcommand=scrollbar.set)
        
        self.dashboard_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        refresh_btn = tk.Button(tab, text="🔄 Refresh Dashboard", command=self.load_dashboard_data,
                               bg=self.primary_color, fg=self.light_color,
                               font=("Arial", 10, "bold"), relief="flat", cursor="hand2",
                               padx=20, pady=8)
        refresh_btn.pack(pady=5)
    
    def load_dashboard_data(self):
        """Load dashboard statistics"""
        if not self.conn:
            return
        try:
            # Count events
            self.cursor.execute("SELECT COUNT(*) as count FROM Events")
            self.dashboard_labels["events"].config(text=str(self.cursor.fetchone()['count']))
            
            # Count active events
            self.cursor.execute("SELECT COUNT(*) as count FROM Events WHERE status='Planned'")
            self.dashboard_labels["active_events"].config(text=str(self.cursor.fetchone()['count']))
            
            # Count venues
            self.cursor.execute("SELECT COUNT(*) as count FROM Venue")
            self.dashboard_labels["venues"].config(text=str(self.cursor.fetchone()['count']))
            
            # Count artists
            self.cursor.execute("SELECT COUNT(*) as count FROM Artist")
            self.dashboard_labels["artists"].config(text=str(self.cursor.fetchone()['count']))
            
            # Count sponsors
            self.cursor.execute("SELECT COUNT(*) as count FROM Sponsor")
            self.dashboard_labels["sponsors"].config(text=str(self.cursor.fetchone()['count']))
            
            # Count staff
            self.cursor.execute("SELECT COUNT(*) as count FROM Staff")
            self.dashboard_labels["staff"].config(text=str(self.cursor.fetchone()['count']))
            
            # Load upcoming events
            self.cursor.execute("""
                SELECT e.eventID, e.name, e.date, v.name as venue, e.status
                FROM Events e
                JOIN Venue v ON e.venueID = v.venueID
                WHERE e.date >= CURDATE()
                ORDER BY e.date
                LIMIT 20
            """)
            events = self.cursor.fetchall()
            
            self.dashboard_tree.delete(*self.dashboard_tree.get_children())
            for event in events:
                self.dashboard_tree.insert("", "end", values=(
                    event['eventID'], event['name'], event['date'],
                    event['venue'], event['status']
                ))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load dashboard: {str(e)}")
    
    def create_events_tab(self):
        """Events CRUD tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="🎫 Events")
        
        # Split into form and list
        paned = ttk.PanedWindow(tab, orient="horizontal")
        paned.pack(fill="both", expand=True, padx=5, pady=5)
        
        form_frame = ttk.LabelFrame(paned, text="📝 Event Details", padding=10)
        list_frame = ttk.LabelFrame(paned, text="📋 Events List", padding=10)
        
        paned.add(form_frame, weight=1)
        paned.add(list_frame, weight=2)
        
        # Form fields
        fields = [
            ("Event ID:", "event_id", "For Update/Delete only"),
            ("Name: *", "event_name", "Required"),
            ("Date (YYYY-MM-DD): *", "event_date", "Format: 2025-12-31"),
            ("Status:", "event_status", "Planned/Completed/Cancelled"),
            ("Start Time (HH:MM:SS): *", "start_time", "Format: 14:30:00"),
            ("End Time (HH:MM:SS): *", "end_time", "Format: 18:00:00"),
            ("Budget: *", "budget", "Must be > 0"),
            ("Venue ID: *", "venue_id", "Select from Venues tab")
        ]
        
        self.event_entries = {}
        for i, (label, key, hint) in enumerate(fields):
            ttk.Label(form_frame, text=label).grid(row=i, column=0, sticky="w", pady=5, padx=5)
            
            if key == "event_status":
                self.event_entries[key] = ttk.Combobox(form_frame, width=30, 
                                                       values=["Planned", "Completed", "Cancelled"])
                self.event_entries[key].set("Planned")
            else:
                self.event_entries[key] = ttk.Entry(form_frame, width=32)
            self.event_entries[key].grid(row=i, column=1, pady=5, padx=5)
            
            tk.Label(form_frame, text=hint, font=("Arial", 8), fg="#7f8c8d", 
                    bg=self.bg_color).grid(row=i, column=2, sticky="w", padx=5)
        
        # Buttons
        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=len(fields)+1, column=0, columnspan=3, pady=20)
        
        buttons = [
            ("➕ Create", self.create_event, self.secondary_color),
            ("✏️ Update", self.update_event, self.warning_color),
            ("🗑️ Delete", self.delete_event, self.accent_color),
            ("🔄 Clear", lambda: self.clear_entries(self.event_entries), "#95a5a6"),
            ("↻ Refresh", self.load_events, self.primary_color)
        ]
        
        for text, cmd, color in buttons:
            btn = tk.Button(btn_frame, text=text, command=cmd, width=12,
                           bg=color, fg=self.light_color,
                           font=("Arial", 9, "bold"), relief="flat", cursor="hand2")
            btn.pack(side="left", padx=3)
        
        # Events list with scrollbar
        tree_scroll = ttk.Frame(list_frame)
        tree_scroll.pack(fill="both", expand=True)
        
        columns = ("ID", "Name", "Date", "Status", "Time", "Budget", "Venue")
        self.events_tree = ttk.Treeview(tree_scroll, columns=columns, show="headings", height=20)
        
        for col in columns:
            self.events_tree.heading(col, text=col)
            self.events_tree.column(col, width=100)
        
        scrollbar = ttk.Scrollbar(tree_scroll, orient="vertical", command=self.events_tree.yview)
        self.events_tree.configure(yscrollcommand=scrollbar.set)
        
        self.events_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.events_tree.bind("<ButtonRelease-1>", self.on_event_select)
        
    def create_venues_tab(self):
        """Venues CRUD tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="🏛️ Venues")
        
        paned = ttk.PanedWindow(tab, orient="horizontal")
        paned.pack(fill="both", expand=True, padx=5, pady=5)
        
        form_frame = ttk.LabelFrame(paned, text="📝 Venue Details", padding=10)
        list_frame = ttk.LabelFrame(paned, text="📋 Venues List", padding=10)
        
        paned.add(form_frame, weight=1)
        paned.add(list_frame, weight=2)
        
        fields = [
            ("Venue ID:", "venue_id"),
            ("Name: *", "venue_name"),
            ("Type: *", "venue_type"),
            ("Address: *", "address"),
            ("Country:", "country"),
            ("Pincode: *", "pincode"),
            ("Capacity: *", "capacity"),
            ("Cost: *", "cost")
        ]
        
        self.venue_entries = {}
        for i, (label, key) in enumerate(fields):
            ttk.Label(form_frame, text=label).grid(row=i, column=0, sticky="w", pady=5, padx=5)
            if key == "venue_type":
                self.venue_entries[key] = ttk.Combobox(form_frame, width=30,
                                                       values=["Indoor", "Outdoor", "Stadium", "Hall", "Theater"])
            else:
                self.venue_entries[key] = ttk.Entry(form_frame, width=32)
                if key == "country":
                    self.venue_entries[key].insert(0, "India")
            self.venue_entries[key].grid(row=i, column=1, pady=5, padx=5)
        
        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=len(fields), column=0, columnspan=2, pady=20)
        
        buttons = [
            ("➕ Create", self.create_venue, self.secondary_color),
            ("✏️ Update", self.update_venue, self.warning_color),
            ("🗑️ Delete", self.delete_venue, self.accent_color),
            ("🔄 Clear", lambda: self.clear_entries(self.venue_entries), "#95a5a6"),
            ("↻ Refresh", self.load_venues, self.primary_color)
        ]
        
        for text, cmd, color in buttons:
            btn = tk.Button(btn_frame, text=text, command=cmd, width=12,
                           bg=color, fg=self.light_color,
                           font=("Arial", 9, "bold"), relief="flat", cursor="hand2")
            btn.pack(side="left", padx=3)
        
        tree_scroll = ttk.Frame(list_frame)
        tree_scroll.pack(fill="both", expand=True)
        
        columns = ("ID", "Name", "Type", "Capacity", "Cost", "Address")
        self.venues_tree = ttk.Treeview(tree_scroll, columns=columns, show="headings", height=20)
        
        for col in columns:
            self.venues_tree.heading(col, text=col)
            self.venues_tree.column(col, width=120)
        
        scrollbar = ttk.Scrollbar(tree_scroll, orient="vertical", command=self.venues_tree.yview)
        self.venues_tree.configure(yscrollcommand=scrollbar.set)
        
        self.venues_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.venues_tree.bind("<ButtonRelease-1>", self.on_venue_select)
        
    def create_artists_tab(self):
        """Artists CRUD tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="🎤 Artists")
        
        paned = ttk.PanedWindow(tab, orient="horizontal")
        paned.pack(fill="both", expand=True, padx=5, pady=5)
        
        form_frame = ttk.LabelFrame(paned, text="📝 Artist Details", padding=10)
        list_frame = ttk.LabelFrame(paned, text="📋 Artists List", padding=10)
        
        paned.add(form_frame, weight=1)
        paned.add(list_frame, weight=2)
        
        fields = [
            ("Artist ID:", "artist_id"),
            ("Name: *", "artist_name"),
            ("Genre: *", "genre"),
            ("Country:", "country"),
            ("Phone: *", "phone"),
            ("Email: *", "email"),
            ("Fee: *", "fee")
        ]
        
        self.artist_entries = {}
        for i, (label, key) in enumerate(fields):
            ttk.Label(form_frame, text=label).grid(row=i, column=0, sticky="w", pady=5, padx=5)
            self.artist_entries[key] = ttk.Entry(form_frame, width=32)
            if key == "country":
                self.artist_entries[key].insert(0, "India")
            self.artist_entries[key].grid(row=i, column=1, pady=5, padx=5)
        
        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=len(fields), column=0, columnspan=2, pady=20)
        
        buttons = [
            ("➕ Create", self.create_artist, self.secondary_color),
            ("✏️ Update", self.update_artist, self.warning_color),
            ("🗑️ Delete", self.delete_artist, self.accent_color),
            ("🔄 Clear", lambda: self.clear_entries(self.artist_entries), "#95a5a6"),
            ("↻ Refresh", self.load_artists, self.primary_color)
        ]
        
        for text, cmd, color in buttons:
            btn = tk.Button(btn_frame, text=text, command=cmd, width=12,
                           bg=color, fg=self.light_color,
                           font=("Arial", 9, "bold"), relief="flat", cursor="hand2")
            btn.pack(side="left", padx=3)
        
        tree_scroll = ttk.Frame(list_frame)
        tree_scroll.pack(fill="both", expand=True)
        
        columns = ("ID", "Name", "Genre", "Country", "Phone", "Fee")
        self.artists_tree = ttk.Treeview(tree_scroll, columns=columns, show="headings", height=20)
        
        for col in columns:
            self.artists_tree.heading(col, text=col)
            self.artists_tree.column(col, width=120)
        
        scrollbar = ttk.Scrollbar(tree_scroll, orient="vertical", command=self.artists_tree.yview)
        self.artists_tree.configure(yscrollcommand=scrollbar.set)
        
        self.artists_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.artists_tree.bind("<ButtonRelease-1>", self.on_artist_select)
    
    def create_sponsors_tab(self):
        """Sponsors CRUD tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="💼 Sponsors")
        
        paned = ttk.PanedWindow(tab, orient="horizontal")
        paned.pack(fill="both", expand=True, padx=5, pady=5)
        
        form_frame = ttk.LabelFrame(paned, text="📝 Sponsor Details", padding=10)
        list_frame = ttk.LabelFrame(paned, text="📋 Sponsors List", padding=10)
        
        paned.add(form_frame, weight=1)
        paned.add(list_frame, weight=2)
        
        fields = [
            ("Sponsor ID:", "sponsor_id"),
            ("Name: *", "sponsor_name"),
            ("Industry:", "industry"),
            ("Contact Person:", "contact_person"),
            ("Phone:", "phone"),
            ("Email:", "email")
        ]
        
        self.sponsor_entries = {}
        for i, (label, key) in enumerate(fields):
            ttk.Label(form_frame, text=label).grid(row=i, column=0, sticky="w", pady=5, padx=5)
            self.sponsor_entries[key] = ttk.Entry(form_frame, width=32)
            self.sponsor_entries[key].grid(row=i, column=1, pady=5, padx=5)
        
        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=len(fields), column=0, columnspan=2, pady=20)
        
        buttons = [
            ("➕ Create", self.create_sponsor, self.secondary_color),
            ("✏️ Update", self.update_sponsor, self.warning_color),
            ("🗑️ Delete", self.delete_sponsor, self.accent_color),
            ("🔄 Clear", lambda: self.clear_entries(self.sponsor_entries), "#95a5a6"),
            ("↻ Refresh", self.load_sponsors, self.primary_color)
        ]
        
        for text, cmd, color in buttons:
            btn = tk.Button(btn_frame, text=text, command=cmd, width=12,
                           bg=color, fg=self.light_color,
                           font=("Arial", 9, "bold"), relief="flat", cursor="hand2")
            btn.pack(side="left", padx=3)
        
        tree_scroll = ttk.Frame(list_frame)
        tree_scroll.pack(fill="both", expand=True)
        
        columns = ("ID", "Name", "Industry", "Contact", "Phone", "Email")
        self.sponsors_tree = ttk.Treeview(tree_scroll, columns=columns, show="headings", height=20)
        
        for col in columns:
            self.sponsors_tree.heading(col, text=col)
            self.sponsors_tree.column(col, width=120)
        
        scrollbar = ttk.Scrollbar(tree_scroll, orient="vertical", command=self.sponsors_tree.yview)
        self.sponsors_tree.configure(yscrollcommand=scrollbar.set)
        
        self.sponsors_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.sponsors_tree.bind("<ButtonRelease-1>", self.on_sponsor_select)
    
    def create_staff_tab(self):
        """Staff CRUD tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="👥 Staff")
        
        paned = ttk.PanedWindow(tab, orient="horizontal")
        paned.pack(fill="both", expand=True, padx=5, pady=5)
        
        form_frame = ttk.LabelFrame(paned, text="📝 Staff Details", padding=10)
        list_frame = ttk.LabelFrame(paned, text="📋 Staff List", padding=10)
        
        paned.add(form_frame, weight=1)
        paned.add(list_frame, weight=2)
        
        fields = [
            ("Staff ID:", "staff_id"),
            ("Name: *", "staff_name"),
            ("Role: *", "role"),
            ("Phone:", "phone"),
            ("Email:", "email"),
            ("Salary:", "salary")
        ]
        
        self.staff_entries = {}
        for i, (label, key) in enumerate(fields):
            ttk.Label(form_frame, text=label).grid(row=i, column=0, sticky="w", pady=5, padx=5)
            if key == "role":
                self.staff_entries[key] = ttk.Combobox(form_frame, width=30,
                                                       values=["Security", "Technician", "Manager", "Volunteer", "Cleaner", "Coordinator"])
            else:
                self.staff_entries[key] = ttk.Entry(form_frame, width=32)
            self.staff_entries[key].grid(row=i, column=1, pady=5, padx=5)
        
        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=len(fields), column=0, columnspan=2, pady=20)
        
        buttons = [
            ("➕ Create", self.create_staff, self.secondary_color),
            ("✏️ Update", self.update_staff, self.warning_color),
            ("🗑️ Delete", self.delete_staff, self.accent_color),
            ("🔄 Clear", lambda: self.clear_entries(self.staff_entries), "#95a5a6"),
            ("↻ Refresh", self.load_staff, self.primary_color)
        ]
        
        for text, cmd, color in buttons:
            btn = tk.Button(btn_frame, text=text, command=cmd, width=12,
                           bg=color, fg=self.light_color,
                           font=("Arial", 9, "bold"), relief="flat", cursor="hand2")
            btn.pack(side="left", padx=3)
        
        tree_scroll = ttk.Frame(list_frame)
        tree_scroll.pack(fill="both", expand=True)
        
        columns = ("ID", "Name", "Role", "Phone", "Email", "Salary")
        self.staff_tree = ttk.Treeview(tree_scroll, columns=columns, show="headings", height=20)
        
        for col in columns:
            self.staff_tree.heading(col, text=col)
            self.staff_tree.column(col, width=120)
        
        scrollbar = ttk.Scrollbar(tree_scroll, orient="vertical", command=self.staff_tree.yview)
        self.staff_tree.configure(yscrollcommand=scrollbar.set)
        
        self.staff_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.staff_tree.bind("<ButtonRelease-1>", self.on_staff_select)
    
    def create_assignments_tab(self):
        """Manage event assignments (artists, sponsors, staff)"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="🔗 Event Assignments")
        
        # Artist assignments
        artist_frame = ttk.LabelFrame(tab, text="🎤 Assign Artist to Event", padding=10)
        artist_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Label(artist_frame, text="Event ID:").grid(row=0, column=0, padx=5, pady=5)
        self.assign_event_artist = ttk.Entry(artist_frame, width=20)
        self.assign_event_artist.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(artist_frame, text="Artist ID:").grid(row=0, column=2, padx=5, pady=5)
        self.assign_artist_id = ttk.Entry(artist_frame, width=20)
        self.assign_artist_id.grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Label(artist_frame, text="No. of Songs:").grid(row=0, column=4, padx=5, pady=5)
        self.assign_songs = ttk.Entry(artist_frame, width=15)
        self.assign_songs.insert(0, "1")
        self.assign_songs.grid(row=0, column=5, padx=5, pady=5)
        
        tk.Button(artist_frame, text="➕ Assign Artist", command=self.assign_artist_to_event,
                 bg=self.secondary_color, fg=self.light_color,
                 font=("Arial", 9, "bold"), relief="flat", cursor="hand2").grid(row=0, column=6, padx=10, pady=5)
        tk.Button(artist_frame, text="❌ Remove Artist", command=self.remove_artist_from_event,
                 bg=self.accent_color, fg=self.light_color,
                 font=("Arial", 9, "bold"), relief="flat", cursor="hand2").grid(row=0, column=7, padx=5, pady=5)
        
        # Sponsor assignments
        sponsor_frame = ttk.LabelFrame(tab, text="💼 Assign Sponsor to Event", padding=10)
        sponsor_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Label(sponsor_frame, text="Event ID:").grid(row=0, column=0, padx=5, pady=5)
        self.assign_event_sponsor = ttk.Entry(sponsor_frame, width=20)
        self.assign_event_sponsor.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(sponsor_frame, text="Sponsor ID:").grid(row=0, column=2, padx=5, pady=5)
        self.assign_sponsor_id = ttk.Entry(sponsor_frame, width=20)
        self.assign_sponsor_id.grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Label(sponsor_frame, text="Amount:").grid(row=0, column=4, padx=5, pady=5)
        self.assign_amount = ttk.Entry(sponsor_frame, width=15)
        self.assign_amount.insert(0, "0")
        self.assign_amount.grid(row=0, column=5, padx=5, pady=5)
        
        tk.Button(sponsor_frame, text="➕ Assign Sponsor", command=self.assign_sponsor_to_event,
                 bg=self.secondary_color, fg=self.light_color,
                 font=("Arial", 9, "bold"), relief="flat", cursor="hand2").grid(row=0, column=6, padx=10, pady=5)
        tk.Button(sponsor_frame, text="❌ Remove Sponsor", command=self.remove_sponsor_from_event,
                 bg=self.accent_color, fg=self.light_color,
                 font=("Arial", 9, "bold"), relief="flat", cursor="hand2").grid(row=0, column=7, padx=5, pady=5)
        
        # Staff assignments
        staff_frame = ttk.LabelFrame(tab, text="👥 Assign Staff to Event", padding=10)
        staff_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Label(staff_frame, text="Event ID:").grid(row=0, column=0, padx=5, pady=5)
        self.assign_event_staff = ttk.Entry(staff_frame, width=20)
        self.assign_event_staff.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(staff_frame, text="Staff ID:").grid(row=0, column=2, padx=5, pady=5)
        self.assign_staff_id = ttk.Entry(staff_frame, width=20)
        self.assign_staff_id.grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Label(staff_frame, text="Shift:").grid(row=0, column=4, padx=5, pady=5)
        self.assign_shift = ttk.Combobox(staff_frame, width=15, 
                                         values=["FULL_DAY", "MORNING", "EVENING", "NIGHT"])
        self.assign_shift.set("FULL_DAY")
        self.assign_shift.grid(row=0, column=5, padx=5, pady=5)
        
        tk.Button(staff_frame, text="➕ Assign Staff", command=self.assign_staff_to_event,
                 bg=self.secondary_color, fg=self.light_color,
                 font=("Arial", 9, "bold"), relief="flat", cursor="hand2").grid(row=0, column=6, padx=10, pady=5)
        tk.Button(staff_frame, text="❌ Remove Staff", command=self.remove_staff_from_event,
                 bg=self.accent_color, fg=self.light_color,
                 font=("Arial", 9, "bold"), relief="flat", cursor="hand2").grid(row=0, column=7, padx=5, pady=5)
        
        # View assignments
        view_frame = ttk.LabelFrame(tab, text="👁️ View Event Assignments", padding=10)
        view_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        control_frame = tk.Frame(view_frame, bg=self.bg_color)
        control_frame.pack(side="top", fill="x", pady=5)
        
        ttk.Label(control_frame, text="Event ID:").pack(side="left", padx=5)
        self.view_assign_event = ttk.Entry(control_frame, width=15)
        self.view_assign_event.pack(side="left", padx=5)
        
        tk.Button(control_frame, text="🎤 View Artists", command=self.view_event_artists,
                 bg=self.warning_color, fg=self.light_color,
                 font=("Arial", 9, "bold"), relief="flat", cursor="hand2").pack(side="left", padx=5)
        tk.Button(control_frame, text="💼 View Sponsors", command=self.view_event_sponsors,
                 bg=self.teal_color, fg=self.light_color,
                 font=("Arial", 9, "bold"), relief="flat", cursor="hand2").pack(side="left", padx=5)
        tk.Button(control_frame, text="👥 View Staff", command=self.view_event_staff,
                 bg=self.purple_color, fg=self.light_color,
                 font=("Arial", 9, "bold"), relief="flat", cursor="hand2").pack(side="left", padx=5)
        
        self.assignments_text = scrolledtext.ScrolledText(view_frame, height=15, width=120,
                                                          bg=self.light_color, fg=self.dark_color,
                                                          font=("Courier", 9))
        self.assignments_text.pack(fill="both", expand=True, pady=10)
    
    def create_reports_tab(self):
        """Reports tab using stored procedures"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="📈 Reports")
        
        controls_frame = ttk.LabelFrame(tab, text="📊 Available Reports", padding=10)
        controls_frame.pack(side="top", fill="x", padx=5, pady=5)
        
        reports = [
            ("📋 Events with Venue & Tickets", "Report_Events_Venue_Tickets", self.primary_color),
            ("🏆 Top 3 Attended Events", "Report_Top_Attended_Events", self.secondary_color),
            ("💰 Sponsor Contributions", "Report_Sponsor_Contributions", self.teal_color),
            ("🎤 Artist Performances", "Report_Artist_Performances", self.warning_color),
            ("👥 Attendee Demographics", "Report_Attendee_Demographics", self.purple_color),
            ("💵 Revenue Per Venue", "Query_Revenue_Per_Venue", "#e67e22")
        ]
        
        for i, (name, proc, color) in enumerate(reports):
            btn = tk.Button(controls_frame, text=name, 
                      command=lambda p=proc: self.run_report(p),
                      bg=color, fg=self.light_color,
                      font=("Arial", 9, "bold"), relief="flat", cursor="hand2",
                      width=30)
            btn.grid(row=i//3, column=i%3, padx=5, pady=5, sticky="ew")
        
        result_frame = ttk.LabelFrame(tab, text="📄 Report Results", padding=10)
        result_frame.pack(side="bottom", fill="both", expand=True, padx=5, pady=5)
        
        self.report_text = scrolledtext.ScrolledText(result_frame, height=25, width=140, 
                                                     font=("Courier", 9),
                                                     bg=self.light_color, fg=self.dark_color)
        self.report_text.pack(fill="both", expand=True)
    
    def create_analytics_tab(self):
        """Analytics tab with functions and procedures"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="📊 Analytics")
        
        # Event analytics section
        event_frame = ttk.LabelFrame(tab, text="🎯 Event Analytics", padding=10)
        event_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Label(event_frame, text="Event ID:").grid(row=0, column=0, padx=5, pady=5)
        self.analytics_event_id = ttk.Entry(event_frame, width=15)
        self.analytics_event_id.insert(0, "1")
        self.analytics_event_id.grid(row=0, column=1, padx=5, pady=5)
        
        analytics_options = [
            ("📊 Full Statistics", "Get_Event_Statistics", self.primary_color),
            ("💰 Financial Summary", "Get_Event_Financial_Summary", self.secondary_color),
            ("💵 Calculate Revenue", "Calculate_Event_Revenue", self.teal_color)
        ]
        
        for i, (name, proc, color) in enumerate(analytics_options):
            btn = tk.Button(event_frame, text=name, 
                      command=lambda p=proc: self.run_event_analytics(p),
                      bg=color, fg=self.light_color,
                      font=("Arial", 9, "bold"), relief="flat", cursor="hand2")
            btn.grid(row=0, column=i+2, padx=5, pady=5)
        
        # Functions section
        func_frame = ttk.LabelFrame(tab, text="⚡ Quick Functions", padding=10)
        func_frame.pack(fill="x", padx=10, pady=10)
        
        functions = [
            ("💵 Revenue", "Get_Event_Revenue", self.secondary_color),
            ("🎫 Tickets Sold", "Get_Tickets_Sold_Count", self.primary_color),
            ("✅ Available Tickets", "Get_Available_Tickets_Count", self.teal_color),
            ("📊 Occupancy %", "Get_Event_Occupancy_Percentage", self.warning_color),
            ("💼 Sponsorship", "Get_Total_Sponsorship", self.purple_color),
            ("🎤 Artist Fees", "Get_Total_Artist_Fees", "#e67e22"),
            ("💰 Net Profit", "Get_Event_Net_Profit", self.secondary_color),
            ("👥 Attendees", "Get_Attendee_Count", self.primary_color),
            ("🎸 Artists", "Get_Artist_Count", self.warning_color)
        ]
        
        for i, (name, func, color) in enumerate(functions):
            btn = tk.Button(func_frame, text=name,
                      command=lambda f=func, n=name: self.run_quick_function(f, n),
                      bg=color, fg=self.light_color,
                      font=("Arial", 9, "bold"), relief="flat", cursor="hand2",
                      width=18)
            btn.grid(row=i//5, column=i%5, padx=5, pady=5)
        
        # Results
        result_frame = ttk.LabelFrame(tab, text="📈 Analytics Results", padding=10)
        result_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.analytics_text = scrolledtext.ScrolledText(result_frame, height=20, width=140, 
                                                       font=("Courier", 9),
                                                       bg=self.light_color, fg=self.dark_color)
        self.analytics_text.pack(fill="both", expand=True)
    
    # CRUD OPERATIONS 
    
    # Events CRUD
    def create_event(self):
        if not self.conn:
            messagebox.showerror("Error", "Please connect to database first!")
            return
        try:
            query = """INSERT INTO Events (name, date, status, start_time, end_time, budget, venueID)
                      VALUES (%s, %s, %s, %s, %s, %s, %s)"""
            values = (
                self.event_entries['event_name'].get(),
                self.event_entries['event_date'].get(),
                self.event_entries['event_status'].get(),
                self.event_entries['start_time'].get(),
                self.event_entries['end_time'].get(),
                float(self.event_entries['budget'].get()),
                int(self.event_entries['venue_id'].get())
            )
            self.cursor.execute(query, values)
            self.conn.commit()
            messagebox.showinfo("Success", f"Event created successfully! ID: {self.cursor.lastrowid}")
            self.load_events()
            self.load_dashboard_data()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create event:\n{str(e)}")
    
    def update_event(self):
        if not self.conn:
            messagebox.showerror("Error", "Please connect to database first!")
            return
        try:
            query = """UPDATE Events SET name=%s, date=%s, status=%s, start_time=%s, 
                      end_time=%s, budget=%s, venueID=%s WHERE eventID=%s"""
            values = (
                self.event_entries['event_name'].get(),
                self.event_entries['event_date'].get(),
                self.event_entries['event_status'].get(),
                self.event_entries['start_time'].get(),
                self.event_entries['end_time'].get(),
                float(self.event_entries['budget'].get()),
                int(self.event_entries['venue_id'].get()),
                int(self.event_entries['event_id'].get())
            )
            self.cursor.execute(query, values)
            self.conn.commit()
            messagebox.showinfo("Success", "Event updated successfully!")
            self.load_events()
            self.load_dashboard_data()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update event:\n{str(e)}")
    
    def delete_event(self):
        if not self.conn:
            messagebox.showerror("Error", "Please connect to database first!")
            return
        try:
            event_id = self.event_entries['event_id'].get()
            if not event_id:
                messagebox.showwarning("Warning", "Please enter Event ID to delete")
                return
            
            if messagebox.askyesno("Confirm", "Are you sure you want to delete this event?\nThis will also delete all related tickets!"):
                query = "DELETE FROM Events WHERE eventID = %s"
                self.cursor.execute(query, (int(event_id),))
                self.conn.commit()
                messagebox.showinfo("Success", "Event deleted successfully!")
                self.clear_entries(self.event_entries)
                self.load_events()
                self.load_dashboard_data()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete event:\n{str(e)}")
    
    def load_events(self):
        if not self.conn:
            return
        try:
            self.cursor.execute("""
                SELECT e.eventID, e.name, e.date, e.status, 
                       CONCAT(e.start_time, '-', e.end_time) as time,
                       e.budget, v.name as venue
                FROM Events e
                JOIN Venue v ON e.venueID = v.venueID
                ORDER BY e.date DESC
            """)
            events = self.cursor.fetchall()
            
            self.events_tree.delete(*self.events_tree.get_children())
            for event in events:
                self.events_tree.insert("", "end", values=(
                    event['eventID'], event['name'], event['date'],
                    event['status'], event['time'], f"₹{event['budget']}", event['venue']
                ))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load events:\n{str(e)}")
    
    def on_event_select(self, event):
        selection = self.events_tree.selection()
        if selection:
            item = self.events_tree.item(selection[0])
            values = item['values']
            
            try:
                self.cursor.execute("SELECT * FROM Events WHERE eventID = %s", (values[0],))
                event_data = self.cursor.fetchone()
                
                self.event_entries['event_id'].delete(0, tk.END)
                self.event_entries['event_id'].insert(0, event_data['eventID'])
                self.event_entries['event_name'].delete(0, tk.END)
                self.event_entries['event_name'].insert(0, event_data['name'])
                self.event_entries['event_date'].delete(0, tk.END)
                self.event_entries['event_date'].insert(0, event_data['date'])
                self.event_entries['event_status'].set(event_data['status'])
                self.event_entries['start_time'].delete(0, tk.END)
                self.event_entries['start_time'].insert(0, str(event_data['start_time']))
                self.event_entries['end_time'].delete(0, tk.END)
                self.event_entries['end_time'].insert(0, str(event_data['end_time']))
                self.event_entries['budget'].delete(0, tk.END)
                self.event_entries['budget'].insert(0, event_data['budget'])
                self.event_entries['venue_id'].delete(0, tk.END)
                self.event_entries['venue_id'].insert(0, event_data['venueID'])
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load event details:\n{str(e)}")
    
    # Venues CRUD
    def create_venue(self):
        if not self.conn:
            messagebox.showerror("Error", "Please connect to database first!")
            return
        try:
            query = """INSERT INTO Venue (name, type, address, country, pincode, capacity, cost)
                      VALUES (%s, %s, %s, %s, %s, %s, %s)"""
            values = (
                self.venue_entries['venue_name'].get(),
                self.venue_entries['venue_type'].get(),
                self.venue_entries['address'].get(),
                self.venue_entries['country'].get(),
                self.venue_entries['pincode'].get(),
                int(self.venue_entries['capacity'].get()),
                float(self.venue_entries['cost'].get())
            )
            self.cursor.execute(query, values)
            self.conn.commit()
            messagebox.showinfo("Success", f"Venue created successfully! ID: {self.cursor.lastrowid}")
            self.load_venues()
            self.load_dashboard_data()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create venue:\n{str(e)}")
    
    def update_venue(self):
        if not self.conn:
            messagebox.showerror("Error", "Please connect to database first!")
            return
        try:
            query = """UPDATE Venue SET name=%s, type=%s, address=%s, country=%s, 
                      pincode=%s, capacity=%s, cost=%s WHERE venueID=%s"""
            values = (
                self.venue_entries['venue_name'].get(),
                self.venue_entries['venue_type'].get(),
                self.venue_entries['address'].get(),
                self.venue_entries['country'].get(),
                self.venue_entries['pincode'].get(),
                int(self.venue_entries['capacity'].get()),
                float(self.venue_entries['cost'].get()),
                int(self.venue_entries['venue_id'].get())
            )
            self.cursor.execute(query, values)
            self.conn.commit()
            messagebox.showinfo("Success", "Venue updated successfully!")
            self.load_venues()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update venue:\n{str(e)}")
    
    def delete_venue(self):
        if not self.conn:
            messagebox.showerror("Error", "Please connect to database first!")
            return
        try:
            venue_id = self.venue_entries['venue_id'].get()
            if not venue_id:
                messagebox.showwarning("Warning", "Please enter Venue ID to delete")
                return
            
            if messagebox.askyesno("Confirm", "Are you sure you want to delete this venue?"):
                query = "DELETE FROM Venue WHERE venueID = %s"
                self.cursor.execute(query, (int(venue_id),))
                self.conn.commit()
                messagebox.showinfo("Success", "Venue deleted successfully!")
                self.clear_entries(self.venue_entries)
                self.load_venues()
                self.load_dashboard_data()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete venue:\n{str(e)}")
    
    def load_venues(self):
        if not self.conn:
            return
        try:
            self.cursor.execute("SELECT * FROM Venue ORDER BY name")
            venues = self.cursor.fetchall()
            
            self.venues_tree.delete(*self.venues_tree.get_children())
            for venue in venues:
                self.venues_tree.insert("", "end", values=(
                    venue['venueID'], venue['name'], venue['type'],
                    venue['capacity'], f"₹{venue['cost']}", venue['address']
                ))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load venues:\n{str(e)}")
    
    def on_venue_select(self, event):
        selection = self.venues_tree.selection()
        if selection:
            item = self.venues_tree.item(selection[0])
            values = item['values']
            
            try:
                self.cursor.execute("SELECT * FROM Venue WHERE venueID = %s", (values[0],))
                venue_data = self.cursor.fetchone()
                
                self.venue_entries['venue_id'].delete(0, tk.END)
                self.venue_entries['venue_id'].insert(0, venue_data['venueID'])
                self.venue_entries['venue_name'].delete(0, tk.END)
                self.venue_entries['venue_name'].insert(0, venue_data['name'])
                self.venue_entries['venue_type'].set(venue_data['type'])
                self.venue_entries['address'].delete(0, tk.END)
                self.venue_entries['address'].insert(0, venue_data['address'])
                self.venue_entries['country'].delete(0, tk.END)
                self.venue_entries['country'].insert(0, venue_data['country'])
                self.venue_entries['pincode'].delete(0, tk.END)
                self.venue_entries['pincode'].insert(0, venue_data['pincode'])
                self.venue_entries['capacity'].delete(0, tk.END)
                self.venue_entries['capacity'].insert(0, venue_data['capacity'])
                self.venue_entries['cost'].delete(0, tk.END)
                self.venue_entries['cost'].insert(0, venue_data['cost'])
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load venue details:\n{str(e)}")
    
    # Artists CRUD
    def create_artist(self):
        if not self.conn:
            messagebox.showerror("Error", "Please connect to database first!")
            return
        try:
            query = """INSERT INTO Artist (name, genre, country, phone_no, email, fee)
                      VALUES (%s, %s, %s, %s, %s, %s)"""
            values = (
                self.artist_entries['artist_name'].get(),
                self.artist_entries['genre'].get(),
                self.artist_entries['country'].get(),
                self.artist_entries['phone'].get(),
                self.artist_entries['email'].get(),
                float(self.artist_entries['fee'].get())
            )
            self.cursor.execute(query, values)
            self.conn.commit()
            messagebox.showinfo("Success", f"Artist created successfully! ID: {self.cursor.lastrowid}")
            self.load_artists()
            self.load_dashboard_data()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create artist:\n{str(e)}")
    
    def update_artist(self):
        if not self.conn:
            messagebox.showerror("Error", "Please connect to database first!")
            return
        try:
            query = """UPDATE Artist SET name=%s, genre=%s, country=%s, phone_no=%s, 
                      email=%s, fee=%s WHERE artistID=%s"""
            values = (
                self.artist_entries['artist_name'].get(),
                self.artist_entries['genre'].get(),
                self.artist_entries['country'].get(),
                self.artist_entries['phone'].get(),
                self.artist_entries['email'].get(),
                float(self.artist_entries['fee'].get()),
                int(self.artist_entries['artist_id'].get())
            )
            self.cursor.execute(query, values)
            self.conn.commit()
            messagebox.showinfo("Success", "Artist updated successfully!")
            self.load_artists()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update artist:\n{str(e)}")
    
    def delete_artist(self):
        if not self.conn:
            messagebox.showerror("Error", "Please connect to database first!")
            return
        try:
            artist_id = self.artist_entries['artist_id'].get()
            if not artist_id:
                messagebox.showwarning("Warning", "Please enter Artist ID to delete")
                return
            
            if messagebox.askyesno("Confirm", "Are you sure you want to delete this artist?"):
                query = "DELETE FROM Artist WHERE artistID = %s"
                self.cursor.execute(query, (int(artist_id),))
                self.conn.commit()
                messagebox.showinfo("Success", "Artist deleted successfully!")
                self.clear_entries(self.artist_entries)
                self.load_artists()
                self.load_dashboard_data()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete artist:\n{str(e)}")
    
    def load_artists(self):
        if not self.conn:
            return
        try:
            self.cursor.execute("SELECT * FROM Artist ORDER BY name")
            artists = self.cursor.fetchall()
            
            self.artists_tree.delete(*self.artists_tree.get_children())
            for artist in artists:
                self.artists_tree.insert("", "end", values=(
                    artist['artistID'], artist['name'], artist['genre'],
                    artist['country'], artist['phone_no'], f"₹{artist['fee']}"
                ))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load artists:\n{str(e)}")
    
    def on_artist_select(self, event):
        selection = self.artists_tree.selection()
        if selection:
            item = self.artists_tree.item(selection[0])
            values = item['values']
            
            try:
                self.cursor.execute("SELECT * FROM Artist WHERE artistID = %s", (values[0],))
                artist_data = self.cursor.fetchone()
                
                self.artist_entries['artist_id'].delete(0, tk.END)
                self.artist_entries['artist_id'].insert(0, artist_data['artistID'])
                self.artist_entries['artist_name'].delete(0, tk.END)
                self.artist_entries['artist_name'].insert(0, artist_data['name'])
                self.artist_entries['genre'].delete(0, tk.END)
                self.artist_entries['genre'].insert(0, artist_data['genre'])
                self.artist_entries['country'].delete(0, tk.END)
                self.artist_entries['country'].insert(0, artist_data['country'])
                self.artist_entries['phone'].delete(0, tk.END)
                self.artist_entries['phone'].insert(0, artist_data['phone_no'])
                self.artist_entries['email'].delete(0, tk.END)
                self.artist_entries['email'].insert(0, artist_data['email'])
                self.artist_entries['fee'].delete(0, tk.END)
                self.artist_entries['fee'].insert(0, artist_data['fee'])
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load artist details:\n{str(e)}")
    
    # Sponsors CRUD
    def create_sponsor(self):
        if not self.conn:
            messagebox.showerror("Error", "Please connect to database first!")
            return
        try:
            query = """INSERT INTO Sponsor (name, industry, contact_person, phone_no, email)
                      VALUES (%s, %s, %s, %s, %s)"""
            values = (
                self.sponsor_entries['sponsor_name'].get(),
                self.sponsor_entries['industry'].get() or None,
                self.sponsor_entries['contact_person'].get() or None,
                self.sponsor_entries['phone'].get() or None,
                self.sponsor_entries['email'].get() or None
            )
            self.cursor.execute(query, values)
            self.conn.commit()
            messagebox.showinfo("Success", f"Sponsor created successfully! ID: {self.cursor.lastrowid}")
            self.load_sponsors()
            self.load_dashboard_data()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create sponsor:\n{str(e)}")
    
    def update_sponsor(self):
        if not self.conn:
            messagebox.showerror("Error", "Please connect to database first!")
            return
        try:
            query = """UPDATE Sponsor SET name=%s, industry=%s, contact_person=%s, 
                      phone_no=%s, email=%s WHERE sponsorID=%s"""
            values = (
                self.sponsor_entries['sponsor_name'].get(),
                self.sponsor_entries['industry'].get() or None,
                self.sponsor_entries['contact_person'].get() or None,
                self.sponsor_entries['phone'].get() or None,
                self.sponsor_entries['email'].get() or None,
                int(self.sponsor_entries['sponsor_id'].get())
            )
            self.cursor.execute(query, values)
            self.conn.commit()
            messagebox.showinfo("Success", "Sponsor updated successfully!")
            self.load_sponsors()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update sponsor:\n{str(e)}")
    
    def delete_sponsor(self):
        if not self.conn:
            messagebox.showerror("Error", "Please connect to database first!")
            return
        try:
            sponsor_id = self.sponsor_entries['sponsor_id'].get()
            if not sponsor_id:
                messagebox.showwarning("Warning", "Please enter Sponsor ID to delete")
                return
            
            if messagebox.askyesno("Confirm", "Are you sure you want to delete this sponsor?"):
                query = "DELETE FROM Sponsor WHERE sponsorID = %s"
                self.cursor.execute(query, (int(sponsor_id),))
                self.conn.commit()
                messagebox.showinfo("Success", "Sponsor deleted successfully!")
                self.clear_entries(self.sponsor_entries)
                self.load_sponsors()
                self.load_dashboard_data()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete sponsor:\n{str(e)}")
    
    def load_sponsors(self):
        if not self.conn:
            return
        try:
            self.cursor.execute("SELECT * FROM Sponsor ORDER BY name")
            sponsors = self.cursor.fetchall()
            
            self.sponsors_tree.delete(*self.sponsors_tree.get_children())
            for sponsor in sponsors:
                self.sponsors_tree.insert("", "end", values=(
                    sponsor['sponsorID'], sponsor['name'], sponsor['industry'] or '',
                    sponsor['contact_person'] or '', sponsor['phone_no'] or '', sponsor['email'] or ''
                ))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load sponsors:\n{str(e)}")
    
    def on_sponsor_select(self, event):
        selection = self.sponsors_tree.selection()
        if selection:
            item = self.sponsors_tree.item(selection[0])
            values = item['values']
            
            try:
                self.cursor.execute("SELECT * FROM Sponsor WHERE sponsorID = %s", (values[0],))
                sponsor_data = self.cursor.fetchone()
                
                self.sponsor_entries['sponsor_id'].delete(0, tk.END)
                self.sponsor_entries['sponsor_id'].insert(0, sponsor_data['sponsorID'])
                self.sponsor_entries['sponsor_name'].delete(0, tk.END)
                self.sponsor_entries['sponsor_name'].insert(0, sponsor_data['name'])
                self.sponsor_entries['industry'].delete(0, tk.END)
                self.sponsor_entries['industry'].insert(0, sponsor_data['industry'] or '')
                self.sponsor_entries['contact_person'].delete(0, tk.END)
                self.sponsor_entries['contact_person'].insert(0, sponsor_data['contact_person'] or '')
                self.sponsor_entries['phone'].delete(0, tk.END)
                self.sponsor_entries['phone'].insert(0, sponsor_data['phone_no'] or '')
                self.sponsor_entries['email'].delete(0, tk.END)
                self.sponsor_entries['email'].insert(0, sponsor_data['email'] or '')
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load sponsor details:\n{str(e)}")
    
    # Staff CRUD
    def create_staff(self):
        if not self.conn:
            messagebox.showerror("Error", "Please connect to database first!")
            return
        try:
            query = """INSERT INTO Staff (name, role, phone_no, email, salary)
                      VALUES (%s, %s, %s, %s, %s)"""
            values = (
                self.staff_entries['staff_name'].get(),
                self.staff_entries['role'].get(),
                self.staff_entries['phone'].get() or None,
                self.staff_entries['email'].get() or None,
                float(self.staff_entries['salary'].get()) if self.staff_entries['salary'].get() else None
            )
            self.cursor.execute(query, values)
            self.conn.commit()
            messagebox.showinfo("Success", f"Staff created successfully! ID: {self.cursor.lastrowid}")
            self.load_staff()
            self.load_dashboard_data()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create staff:\n{str(e)}")
    
    def update_staff(self):
        if not self.conn:
            messagebox.showerror("Error", "Please connect to database first!")
            return
        try:
            query = """UPDATE Staff SET name=%s, role=%s, phone_no=%s, email=%s, salary=%s WHERE staffID=%s"""
            values = (
                self.staff_entries['staff_name'].get(),
                self.staff_entries['role'].get(),
                self.staff_entries['phone'].get() or None,
                self.staff_entries['email'].get() or None,
                float(self.staff_entries['salary'].get()) if self.staff_entries['salary'].get() else None,
                int(self.staff_entries['staff_id'].get())
            )
            self.cursor.execute(query, values)
            self.conn.commit()
            messagebox.showinfo("Success", "Staff updated successfully!")
            self.load_staff()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update staff:\n{str(e)}")
    
    def delete_staff(self):
        if not self.conn:
            messagebox.showerror("Error", "Please connect to database first!")
            return
        try:
            staff_id = self.staff_entries['staff_id'].get()
            if not staff_id:
                messagebox.showwarning("Warning", "Please enter Staff ID to delete")
                return
            
            if messagebox.askyesno("Confirm", "Are you sure you want to delete this staff member?"):
                query = "DELETE FROM Staff WHERE staffID = %s"
                self.cursor.execute(query, (int(staff_id),))
                self.conn.commit()
                messagebox.showinfo("Success", "Staff deleted successfully!")
                self.clear_entries(self.staff_entries)
                self.load_staff()
                self.load_dashboard_data()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete staff:\n{str(e)}")
    
    def load_staff(self):
        if not self.conn:
            return
        try:
            self.cursor.execute("SELECT * FROM Staff ORDER BY role, name")
            staff = self.cursor.fetchall()
            
            self.staff_tree.delete(*self.staff_tree.get_children())
            for s in staff:
                self.staff_tree.insert("", "end", values=(
                    s['staffID'], s['name'], s['role'],
                    s['phone_no'] or '', s['email'] or '', 
                    f"₹{s['salary']}" if s['salary'] else ''
                ))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load staff:\n{str(e)}")
    
    def on_staff_select(self, event):
        selection = self.staff_tree.selection()
        if selection:
            item = self.staff_tree.item(selection[0])
            values = item['values']
            
            try:
                self.cursor.execute("SELECT * FROM Staff WHERE staffID = %s", (values[0],))
                staff_data = self.cursor.fetchone()
                
                self.staff_entries['staff_id'].delete(0, tk.END)
                self.staff_entries['staff_id'].insert(0, staff_data['staffID'])
                self.staff_entries['staff_name'].delete(0, tk.END)
                self.staff_entries['staff_name'].insert(0, staff_data['name'])
                self.staff_entries['role'].set(staff_data['role'])
                self.staff_entries['phone'].delete(0, tk.END)
                self.staff_entries['phone'].insert(0, staff_data['phone_no'] or '')
                self.staff_entries['email'].delete(0, tk.END)
                self.staff_entries['email'].insert(0, staff_data['email'] or '')
                self.staff_entries['salary'].delete(0, tk.END)
                self.staff_entries['salary'].insert(0, staff_data['salary'] or '')
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load staff details:\n{str(e)}")
    
    # ASSIGNMENT OPERATIONS
    
    def assign_artist_to_event(self):
        if not self.conn:
            messagebox.showerror("Error", "Please connect to database first!")
            return
        try:
            query = "INSERT INTO performs (artistID, eventID, noOfSongs) VALUES (%s, %s, %s)"
            values = (
                int(self.assign_artist_id.get()),
                int(self.assign_event_artist.get()),
                int(self.assign_songs.get())
            )
            self.cursor.execute(query, values)
            self.conn.commit()
            messagebox.showinfo("Success", "Artist assigned to event successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to assign artist:\n{str(e)}")
    
    def remove_artist_from_event(self):
        if not self.conn:
            messagebox.showerror("Error", "Please connect to database first!")
            return
        try:
            query = "DELETE FROM performs WHERE artistID = %s AND eventID = %s"
            values = (
                int(self.assign_artist_id.get()),
                int(self.assign_event_artist.get())
            )
            self.cursor.execute(query, values)
            self.conn.commit()
            messagebox.showinfo("Success", "Artist removed from event successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to remove artist:\n{str(e)}")
    
    def assign_sponsor_to_event(self):
        if not self.conn:
            messagebox.showerror("Error", "Please connect to database first!")
            return
        try:
            query = "INSERT INTO sponsors_event (sponsorID, eventID, amount) VALUES (%s, %s, %s)"
            values = (
                int(self.assign_sponsor_id.get()),
                int(self.assign_event_sponsor.get()),
                float(self.assign_amount.get())
            )
            self.cursor.execute(query, values)
            self.conn.commit()
            messagebox.showinfo("Success", "Sponsor assigned to event successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to assign sponsor:\n{str(e)}")
    
    def remove_sponsor_from_event(self):
        if not self.conn:
            messagebox.showerror("Error", "Please connect to database first!")
            return
        try:
            query = "DELETE FROM sponsors_event WHERE sponsorID = %s AND eventID = %s"
            values = (
                int(self.assign_sponsor_id.get()),
                int(self.assign_event_sponsor.get())
            )
            self.cursor.execute(query, values)
            self.conn.commit()
            messagebox.showinfo("Success", "Sponsor removed from event successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to remove sponsor:\n{str(e)}")
    
    def assign_staff_to_event(self):
        if not self.conn:
            messagebox.showerror("Error", "Please connect to database first!")
            return
        try:
            query = "INSERT INTO works_at (staffID, eventID, shift) VALUES (%s, %s, %s)"
            values = (
                int(self.assign_staff_id.get()),
                int(self.assign_event_staff.get()),
                self.assign_shift.get()
            )
            self.cursor.execute(query, values)
            self.conn.commit()
            messagebox.showinfo("Success", "Staff assigned to event successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to assign staff:\n{str(e)}")
    
    def remove_staff_from_event(self):
        if not self.conn:
            messagebox.showerror("Error", "Please connect to database first!")
            return
        try:
            query = "DELETE FROM works_at WHERE staffID = %s AND eventID = %s"
            values = (
                int(self.assign_staff_id.get()),
                int(self.assign_event_staff.get())
            )
            self.cursor.execute(query, values)
            self.conn.commit()
            messagebox.showinfo("Success", "Staff removed from event successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to remove staff:\n{str(e)}")
    
    def view_event_artists(self):
        if not self.conn:
            messagebox.showerror("Error", "Please connect to database first!")
            return
        try:
            event_id = int(self.view_assign_event.get())
            self.cursor.callproc("Get_Event_Artists", [event_id])
            
            self.assignments_text.delete(1.0, tk.END)
            self.assignments_text.insert(tk.END, f"=== Artists for Event {event_id} ===\n\n")
            
            for result in self.cursor.stored_results():
                rows = result.fetchall()
                if rows:
                    self.assignments_text.insert(tk.END, f"{'ID':<5} {'Name':<30} {'Genre':<20} {'Songs':<10} {'Fee':<15}\n")
                    self.assignments_text.insert(tk.END, "-" * 85 + "\n")
                    
                    for row in rows:
                        self.assignments_text.insert(tk.END, 
                            f"{row['artistID']:<5} {row['name']:<30} {row['genre']:<20} "
                            f"{row['noOfSongs']:<10} ₹{row['fee']:<14.2f}\n")
                    self.assignments_text.insert(tk.END, f"\nTotal Artists: {len(rows)}\n")
                else:
                    self.assignments_text.insert(tk.END, "No artists assigned to this event.\n")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to view artists:\n{str(e)}")
    
    def view_event_sponsors(self):
        if not self.conn:
            messagebox.showerror("Error", "Please connect to database first!")
            return
        try:
            event_id = int(self.view_assign_event.get())
            self.cursor.callproc("Get_Event_Sponsors", [event_id])
            
            self.assignments_text.delete(1.0, tk.END)
            self.assignments_text.insert(tk.END, f"=== Sponsors for Event {event_id} ===\n\n")
            
            total_amount = 0
            for result in self.cursor.stored_results():
                rows = result.fetchall()
                if rows:
                    self.assignments_text.insert(tk.END, f"{'ID':<5} {'Name':<30} {'Industry':<20} {'Amount':<15}\n")
                    self.assignments_text.insert(tk.END, "-" * 75 + "\n")
                    
                    for row in rows:
                        total_amount += row['amount']
                        self.assignments_text.insert(tk.END, 
                            f"{row['sponsorID']:<5} {row['name']:<30} {row['industry'] or 'N/A':<20} "
                            f"₹{row['amount']:<14.2f}\n")
                    self.assignments_text.insert(tk.END, f"\nTotal Sponsors: {len(rows)}\n")
                    self.assignments_text.insert(tk.END, f"Total Sponsorship Amount: ₹{total_amount:,.2f}\n")
                else:
                    self.assignments_text.insert(tk.END, "No sponsors assigned to this event.\n")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to view sponsors:\n{str(e)}")
    
    def view_event_staff(self):
        if not self.conn:
            messagebox.showerror("Error", "Please connect to database first!")
            return
        try:
            event_id = int(self.view_assign_event.get())
            self.cursor.callproc("Get_Event_Staff", [event_id])
            
            self.assignments_text.delete(1.0, tk.END)
            self.assignments_text.insert(tk.END, f"=== Staff for Event {event_id} ===\n\n")
            
            for result in self.cursor.stored_results():
                rows = result.fetchall()
                if rows:
                    self.assignments_text.insert(tk.END, f"{'ID':<5} {'Name':<30} {'Role':<20} {'Shift':<15} {'Salary':<15}\n")
                    self.assignments_text.insert(tk.END, "-" * 90 + "\n")
                    
                    for row in rows:
                        self.assignments_text.insert(tk.END, 
                            f"{row['staffID']:<5} {row['name']:<30} {row['role']:<20} "
                            f"{row['shift']:<15} ₹{row['salary'] or 0:<14.2f}\n")
                    self.assignments_text.insert(tk.END, f"\nTotal Staff: {len(rows)}\n")
                else:
                    self.assignments_text.insert(tk.END, "No staff assigned to this event.\n")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to view staff:\n{str(e)}")
    
    #  REPORTS & ANALYTICS 
    
    def run_report(self, procedure_name):
        if not self.conn:
            messagebox.showerror("Error", "Please connect to database first!")
            return
        try:
            self.cursor.callproc(procedure_name)
            
            self.report_text.delete(1.0, tk.END)
            self.report_text.insert(tk.END, f"{'='*100}\n")
            self.report_text.insert(tk.END, f"{procedure_name.replace('_', ' ').upper()}\n")
            self.report_text.insert(tk.END, f"{'='*100}\n\n")
            
            for result in self.cursor.stored_results():
                rows = result.fetchall()
                if rows:
                    # Get column names
                    columns = result.column_names
                    
                    # Calculate column widths
                    col_widths = {}
                    for col in columns:
                        col_widths[col] = max(len(str(col)), 15)
                    
                    # Header
                    header = " | ".join(str(col).ljust(col_widths[col]) for col in columns)
                    self.report_text.insert(tk.END, header + "\n")
                    self.report_text.insert(tk.END, "-" * len(header) + "\n")
                    
                    # Data rows
                    for row in rows:
                        row_str = " | ".join(str(v if v is not None else '').ljust(col_widths[k]) 
                                            for k, v in row.items())
                        self.report_text.insert(tk.END, row_str + "\n")
                    
                    self.report_text.insert(tk.END, f"\n{len(rows)} rows returned.\n\n")
                else:
                    self.report_text.insert(tk.END, "No data found.\n\n")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to run report:\n{str(e)}")
            self.report_text.insert(tk.END, f"Error: {str(e)}\n")
    
    def run_event_analytics(self, procedure_name):
        if not self.conn:
            messagebox.showerror("Error", "Please connect to database first!")
            return
        try:
            event_id = int(self.analytics_event_id.get())
            # Close existing result sets to avoid "Unread result found" error
            try:
                self.cursor.fetchall()
            except:
                pass
            # Create a new cursor for the procedure call
            proc_cursor = self.conn.cursor(dictionary=True)
            proc_cursor.callproc(procedure_name, [event_id])
            
            self.analytics_text.delete(1.0, tk.END)
            self.analytics_text.insert(tk.END, f"{'='*100}\n")
            self.analytics_text.insert(tk.END, f"{procedure_name.replace('_', ' ').upper()} - Event ID: {event_id}\n")
            self.analytics_text.insert(tk.END, f"{'='*100}\n\n")
            
            for result in proc_cursor.stored_results():
                rows = result.fetchall()
                if rows:
                    for row in rows:
                        for key, value in row.items():
                            self.analytics_text.insert(tk.END, f"{key:.<40} {value}\n")
                        self.analytics_text.insert(tk.END, "\n")
                else:
                    self.analytics_text.insert(tk.END, "No data found.\n\n")
            
            proc_cursor.close()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to run analytics:\n{str(e)}")
            self.analytics_text.insert(tk.END, f"Error: {str(e)}\n")
    
    def run_quick_function(self, function_name, display_name):
        if not self.conn:
            messagebox.showerror("Error", "Please connect to database first!")
            return
        try:
            event_id = int(self.analytics_event_id.get())
            
            # Create fresh cursor for function call
            func_cursor = self.conn.cursor(dictionary=True)
            query = f"SELECT {function_name}(%s) AS result"
            func_cursor.execute(query, (event_id,))
            result = func_cursor.fetchone()
            
            self.analytics_text.delete(1.0, tk.END)
            self.analytics_text.insert(tk.END, f"{'='*60}\n")
            self.analytics_text.insert(tk.END, f"{display_name} - Event ID: {event_id}\n")
            self.analytics_text.insert(tk.END, f"{'='*60}\n\n")
            
            # Format result based on function type
            result_value = result['result']
            if function_name in ['Get_Event_Revenue', 'Get_Total_Sponsorship', 'Get_Total_Artist_Fees', 'Get_Event_Net_Profit']:
                self.analytics_text.insert(tk.END, f"Result: ₹{result_value:,.2f}\n")
            elif function_name == 'Get_Event_Occupancy_Percentage':
                self.analytics_text.insert(tk.END, f"Result: {result_value:.2f}%\n")
            else:
                self.analytics_text.insert(tk.END, f"Result: {result_value}\n")
            
            # Show additional context
            func_cursor.execute("SELECT name, date, status FROM Events WHERE eventID = %s", (event_id,))
            event_info = func_cursor.fetchone()
            if event_info:
                self.analytics_text.insert(tk.END, f"\nEvent Details:\n")
                self.analytics_text.insert(tk.END, f"  Name: {event_info['name']}\n")
                self.analytics_text.insert(tk.END, f"  Date: {event_info['date']}\n")
                self.analytics_text.insert(tk.END, f"  Status: {event_info['status']}\n")
            
            func_cursor.close()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to run function:\n{str(e)}")
            self.analytics_text.insert(tk.END, f"Error: {str(e)}\n")
    
    # UTILITY FUNCTIONS 
    
    def clear_entries(self, entries_dict):
        for entry in entries_dict.values():
            if isinstance(entry, ttk.Entry):
                entry.delete(0, tk.END)
            elif isinstance(entry, ttk.Combobox):
                entry.set("")
    
    def __del__(self):
        if self.conn:
            self.cursor.close()
            self.conn.close()


if __name__ == "__main__":
    root = tk.Tk()
    app = EventManagementAdminGUI(root)
    root.mainloop()