
-- Create database
CREATE DATABASE IF NOT EXISTS evm3;
USE evm3;

-- TABLE DEFINITIONS

-- Create Venue table
CREATE TABLE Venue (
    venueID INT PRIMARY KEY AUTO_INCREMENT,
    cost DECIMAL(10,2) NOT NULL CHECK (cost >= 0),
    address VARCHAR(255) NOT NULL,
    country VARCHAR(100) NOT NULL DEFAULT 'India',
    pincode VARCHAR(20) NOT NULL,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(100) NOT NULL CHECK (type IN ('Indoor', 'Outdoor', 'Stadium', 'Hall', 'Theater')),
    capacity INT NOT NULL CHECK (capacity > 0)
);

-- Create Events table
CREATE TABLE Events (
    eventID INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    date DATE NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'Planned' CHECK (status IN ('Planned', 'Completed', 'Cancelled')),
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    budget DECIMAL(10,2) NOT NULL CHECK (budget > 0),
    venueID INT NOT NULL,
    completion_time TIMESTAMP NULL,
    FOREIGN KEY (venueID) REFERENCES Venue(venueID) ON DELETE CASCADE ON UPDATE CASCADE,
    CHECK (end_time > start_time)
);

-- Create Ticket table
CREATE TABLE Ticket (
    ticketID INT PRIMARY KEY AUTO_INCREMENT,
    price DECIMAL(10,2) NOT NULL CHECK (price > 0),
    status VARCHAR(50) NOT NULL DEFAULT 'AVAILABLE' CHECK (status IN ('AVAILABLE','SOLD')),
    type VARCHAR(100) NOT NULL CHECK (type IN ('VIP','PREMIUM','GENERAL','STUDENT')),
    seatNo VARCHAR(20) NOT NULL,
    eventID INT NOT NULL,
    FOREIGN KEY (eventID) REFERENCES Events(eventID) ON DELETE CASCADE ON UPDATE CASCADE,
    UNIQUE KEY unique_seat_per_event (eventID, seatNo)
);

-- Create Attendee table
CREATE TABLE Attendee (
    attendeeID INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    phone_no VARCHAR(20) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    gender VARCHAR(10) CHECK (gender IN ('M','F','O')),
    age INT CHECK (age BETWEEN 5 AND 80)
);

-- Create Artist table
CREATE TABLE Artist (
    artistID INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    genre VARCHAR(100) NOT NULL,
    country VARCHAR(100) NOT NULL DEFAULT 'INDIA',
    phone_no VARCHAR(20) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    fee DECIMAL(10,2) NOT NULL CHECK(fee >= 0)
);

-- Create social_media table
CREATE TABLE social_media (
    artistID INT,
    social_media_link VARCHAR(255) NOT NULL,
    PRIMARY KEY (artistID, social_media_link),
    FOREIGN KEY (artistID) REFERENCES Artist(artistID) ON DELETE CASCADE ON UPDATE CASCADE
);

-- Create performs relationship table
CREATE TABLE performs (
    artistID INT NOT NULL,
    eventID INT NOT NULL,
    noOfSongs INT DEFAULT 1 CHECK(noOfSongs > 0),
    PRIMARY KEY (artistID, eventID),
    FOREIGN KEY (artistID) REFERENCES Artist(artistID) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (eventID) REFERENCES Events(eventID) ON DELETE CASCADE ON UPDATE CASCADE
);

-- Create purchases relationship table
CREATE TABLE purchases (
    attendeeID INT NOT NULL,
    ticketID INT NOT NULL,
    PRIMARY KEY (attendeeID, ticketID),
    FOREIGN KEY (attendeeID) REFERENCES Attendee(attendeeID) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (ticketID) REFERENCES Ticket(ticketID) ON DELETE CASCADE ON UPDATE CASCADE
);

-- Create attends relationship table
CREATE TABLE attends (
    attendeeID INT NOT NULL,
    eventID INT NOT NULL,
    PRIMARY KEY (attendeeID, eventID),
    FOREIGN KEY (attendeeID) REFERENCES Attendee(attendeeID) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (eventID) REFERENCES Events(eventID) ON DELETE CASCADE ON UPDATE CASCADE
);

-- Create Sponsor table
CREATE TABLE Sponsor (
    sponsorID INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    industry VARCHAR(100),
    contact_person VARCHAR(255),
    phone_no VARCHAR(20),
    email VARCHAR(255) UNIQUE
);

-- Sponsor ↔ Event (Many-to-Many)
CREATE TABLE sponsors_event (
    sponsorID INT NOT NULL,
    eventID INT NOT NULL,
    amount DECIMAL(10,2) NOT NULL CHECK(amount >= 0),
    PRIMARY KEY (sponsorID, eventID),
    FOREIGN KEY (sponsorID) REFERENCES Sponsor(sponsorID) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (eventID) REFERENCES Events(eventID) ON DELETE CASCADE ON UPDATE CASCADE
);

-- Create Staff table
CREATE TABLE Staff (
    staffID INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    role VARCHAR(100) NOT NULL CHECK(role IN ('Security','Technician','Manager','Volunteer','Cleaner','Coordinator')),
    phone_no VARCHAR(20) UNIQUE,
    email VARCHAR(255) UNIQUE,
    salary DECIMAL(10,2) CHECK(salary >= 0)
);

-- Staff ↔ Event (Many-to-Many)
CREATE TABLE works_at (
    staffID INT NOT NULL,
    eventID INT NOT NULL,
    shift VARCHAR(50) DEFAULT 'FULL_DAY' CHECK(shift IN ('FULL_DAY','MORNING','EVENING','NIGHT')),
    PRIMARY KEY (staffID, eventID),
    FOREIGN KEY (staffID) REFERENCES Staff(staffID) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (eventID) REFERENCES Events(eventID) ON DELETE CASCADE ON UPDATE CASCADE
);



-- TRIGGERS - DATA INTEGRITY & BUSINESS LOGIC

-- 1. Prevent venue double booking (time clash prevention)
DELIMITER //
CREATE TRIGGER prevent_venue_time_clash
BEFORE INSERT ON Events
FOR EACH ROW
BEGIN
    DECLARE clash_count INT;
    
    -- Check if there's any event at the same venue on the same date with overlapping times
    SELECT COUNT(*) INTO clash_count
    FROM Events
    WHERE venueID = NEW.venueID
    AND date = NEW.date
    AND status != 'Cancelled'
    AND (
        -- New event starts during existing event
        (NEW.start_time >= start_time AND NEW.start_time < end_time)
        OR
        -- New event ends during existing event
        (NEW.end_time > start_time AND NEW.end_time <= end_time)
        OR
        -- New event completely encompasses existing event
        (NEW.start_time <= start_time AND NEW.end_time >= end_time)
    );
    
    IF clash_count > 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Venue time clash: This venue is already booked for an overlapping time slot on this date';
    END IF;
END //
DELIMITER ;

-- 2. Prevent venue double booking on UPDATE
DELIMITER //
CREATE TRIGGER prevent_venue_time_clash_update
BEFORE UPDATE ON Events
FOR EACH ROW
BEGIN
    DECLARE clash_count INT;
    
    -- Only check if venue, date, or times are being changed
    IF (NEW.venueID != OLD.venueID OR NEW.date != OLD.date OR 
        NEW.start_time != OLD.start_time OR NEW.end_time != OLD.end_time) THEN
        
        SELECT COUNT(*) INTO clash_count
        FROM Events
        WHERE venueID = NEW.venueID
        AND date = NEW.date
        AND eventID != NEW.eventID  -- Exclude current event
        AND status != 'Cancelled'
        AND (
            (NEW.start_time >= start_time AND NEW.start_time < end_time)
            OR
            (NEW.end_time > start_time AND NEW.end_time <= end_time)
            OR
            (NEW.start_time <= start_time AND NEW.end_time >= end_time)
        );
        
        IF clash_count > 0 THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Venue time clash: This venue is already booked for an overlapping time slot on this date';
        END IF;
    END IF;
END //
DELIMITER ;

-- 3. Auto update ticket status when purchased
DELIMITER //
CREATE TRIGGER auto_ticket_sold_status
AFTER INSERT ON purchases
FOR EACH ROW
BEGIN
    UPDATE Ticket
    SET status = 'SOLD'
    WHERE ticketID = NEW.ticketID;
END //
DELIMITER ;

-- 4. Prevent selling already sold tickets
DELIMITER //
CREATE TRIGGER prevent_duplicate_ticket_sale
BEFORE INSERT ON purchases
FOR EACH ROW
BEGIN
    DECLARE ticket_status VARCHAR(50);
    
    SELECT status INTO ticket_status
    FROM Ticket
    WHERE ticketID = NEW.ticketID;
    
    IF ticket_status = 'SOLD' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Cannot purchase ticket: This ticket has already been sold';
    END IF;
END //
DELIMITER ;

-- 5. Prevent overbooking venue capacity
DELIMITER //
CREATE TRIGGER prevent_overbooking
BEFORE INSERT ON attends
FOR EACH ROW
BEGIN
    DECLARE venue_cap INT;
    DECLARE current_attendees INT;
    
    -- Get venue capacity
    SELECT v.capacity INTO venue_cap
    FROM Events e
    JOIN Venue v ON e.venueID = v.venueID
    WHERE e.eventID = NEW.eventID;
    
    -- Get current attendee count
    SELECT COUNT(*) INTO current_attendees
    FROM attends
    WHERE eventID = NEW.eventID;
    
    -- Check if adding this attendee would exceed capacity
    IF current_attendees >= venue_cap THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Cannot add attendee: Venue capacity exceeded';
    END IF;
END //
DELIMITER ;

-- 6. Log event completion time
DELIMITER //
CREATE TRIGGER log_event_completion_time
BEFORE UPDATE ON Events
FOR EACH ROW
BEGIN
    IF NEW.status = 'Completed' AND OLD.status != 'Completed' THEN
        SET NEW.completion_time = NOW();
    END IF;
END //
DELIMITER ;

-- 7. Prevent duplicate artist performance at same event
DELIMITER //
CREATE TRIGGER prevent_duplicate_artist_performance
BEFORE INSERT ON performs
FOR EACH ROW
BEGIN
    DECLARE perf_count INT;
    
    SELECT COUNT(*) INTO perf_count
    FROM performs
    WHERE artistID = NEW.artistID AND eventID = NEW.eventID;
    
    IF perf_count > 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Duplicate entry: This artist is already scheduled to perform at this event';
    END IF;
END //
DELIMITER ;

-- 8. Prevent duplicate staff assignment
DELIMITER //
CREATE TRIGGER prevent_duplicate_staff_assignment
BEFORE INSERT ON works_at
FOR EACH ROW
BEGIN
    DECLARE assignment_count INT;
    
    SELECT COUNT(*) INTO assignment_count
    FROM works_at
    WHERE staffID = NEW.staffID AND eventID = NEW.eventID;
    
    IF assignment_count > 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Duplicate entry: This staff member is already assigned to this event';
    END IF;
END //
DELIMITER ;

-- 9. Prevent duplicate sponsor for same event
DELIMITER //
CREATE TRIGGER prevent_duplicate_sponsor
BEFORE INSERT ON sponsors_event
FOR EACH ROW
BEGIN
    DECLARE sponsor_count INT;
    
    SELECT COUNT(*) INTO sponsor_count
    FROM sponsors_event
    WHERE sponsorID = NEW.sponsorID AND eventID = NEW.eventID;
    
    IF sponsor_count > 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Duplicate entry: This sponsor is already linked to this event';
    END IF;
END //
DELIMITER ;

DELIMITER //

CREATE TRIGGER trg_after_event_insert
AFTER INSERT ON Events
FOR EACH ROW
BEGIN
    DECLARE total_capacity INT;
    DECLARE vip_capacity INT;
    DECLARE premium_capacity INT;
    DECLARE general_capacity INT;
    DECLARE student_capacity INT;
    DECLARE seat_no INT DEFAULT 1;

    -- Get the venue's capacity for the new event
    SELECT capacity INTO total_capacity
    FROM Venue
    WHERE venueID = NEW.venueID;

    -- Define the number of tickets per category
    SET vip_capacity = total_capacity * 0.1; -- 10% VIP
    SET premium_capacity = total_capacity * 0.2; -- 20% PREMIUM
    SET general_capacity = total_capacity * 0.5; -- 50% GENERAL
    SET student_capacity = total_capacity * 0.2; -- 20% STUDENT

    -- Insert VIP tickets
    WHILE vip_capacity > 0 DO
        INSERT INTO Ticket (price, status, type, seatNo, eventID)
        VALUES (1000.00, 'AVAILABLE', 'VIP', CONCAT('VIP-', seat_no), NEW.eventID);
        SET seat_no = seat_no + 1;
        SET vip_capacity = vip_capacity - 1;
    END WHILE;

    -- Insert PREMIUM tickets
    WHILE premium_capacity > 0 DO
        INSERT INTO Ticket (price, status, type, seatNo, eventID)
        VALUES (750.00, 'AVAILABLE', 'PREMIUM', CONCAT('PREMIUM-', seat_no), NEW.eventID);
        SET seat_no = seat_no + 1;
        SET premium_capacity = premium_capacity - 1;
    END WHILE;

    -- Insert GENERAL tickets
    WHILE general_capacity > 0 DO
        INSERT INTO Ticket (price, status, type, seatNo, eventID)
        VALUES (500.00, 'AVAILABLE', 'GENERAL', CONCAT('GENERAL-', seat_no), NEW.eventID);
        SET seat_no = seat_no + 1;
        SET general_capacity = general_capacity - 1;
    END WHILE;

    -- Insert STUDENT tickets
    WHILE student_capacity > 0 DO
        INSERT INTO Ticket (price, status, type, seatNo, eventID)
        VALUES (250.00, 'AVAILABLE', 'STUDENT', CONCAT('STUDENT-', seat_no), NEW.eventID);
        SET seat_no = seat_no + 1;
        SET student_capacity = student_capacity - 1;
    END WHILE;

END //

DELIMITER ;

-- SAMPLE DATA INSERTION

INSERT INTO Venue (cost, address, country, pincode, name, type, capacity)
VALUES
(50000, 'MG Road, Bengaluru', 'India', '560001', 'Bangalore Convention Center', 'Indoor', 5),
(50000, 'MG Road, Bengaluru', 'India', '560001', 'Bangalore Convention Center', 'Indoor', 5),
(30000, 'Marine Drive, Mumbai', 'India', '400001', 'Mumbai Beach Arena', 'Outdoor', 10),
(75000, 'Connaught Place, New Delhi', 'India', '110001', 'Delhi Grand Hall', 'Hall', 10),
(60000, 'Park Street, Kolkata', 'India', '700016', 'Kolkata Royal Theater', 'Theater', 5);

INSERT INTO Events (name, date, status, start_time, end_time, budget, venueID)
VALUES
('Rock Night', '2025-12-10', 'Planned', '18:00:00', '23:00:00', 200000, 2),
('Tech Conference 2025', '2025-11-20', 'Planned', '09:00:00', '17:00:00', 500000, 1),
('Classical Music Gala', '2025-12-15', 'Planned', '19:00:00', '22:00:00', 150000, 4),
('Startup Pitch Fest', '2025-11-25', 'Planned', '10:00:00', '16:00:00', 300000, 3);

INSERT INTO Artist (name, genre, country, phone_no, email, fee)
VALUES
('Arijit Singh', 'Music', 'India', '9990011223', 'arijit@example.com', 100000),
('Sunidhi Chauhan', 'Music', 'India', '8882233445', 'sunidhi@example.com', 80000),
('Vir Das', 'Comedy', 'India', '7773344556', 'vir@example.com', 60000),
('Shankar Mahadevan', 'Music', 'India', '9999988877', 'shankar@example.com', 90000);

INSERT INTO social_media (artistID, social_media_link)
VALUES
(1, 'https://instagram.com/arijitsingh'),
(2, 'https://twitter.com/sunidhichauhan'),
(3, 'https://instagram.com/virdas'),
(4, 'https://facebook.com/shankarmahadevan');

INSERT INTO Attendee (name, phone_no, email, gender, age)
VALUES
('Ravi Kumar', '9876543210', 'ravi.kumar@example.com', 'M', 28),
('Priya Sharma', '9765432109', 'priya.sharma@example.com', 'F', 24),
('Ankit Mehta', '9654321098', 'ankit.mehta@example.com', 'M', 32),
('Neha Gupta', '9543210987', 'neha.gupta@example.com', 'F', 26);

INSERT INTO performs (artistID, eventID, noOfSongs)
VALUES
(1, 1, 10),
(2, 1, 8),
(4, 3, 6),
(3, 4, 1);

INSERT INTO attends (attendeeID, eventID)
VALUES
(1, 1),
(2, 2),
(3, 3),
(4, 4);

INSERT INTO Sponsor (name, industry, contact_person, phone_no, email)
VALUES
('Tata Motors', 'Automobile', 'Rohit Singh', '9988776655', 'tata.sponsor@example.com'),
('HDFC Bank', 'Finance', 'Meena Rao', '8877665544', 'hdfc@example.com'),
('Red Bull', 'Beverages', 'Raj Patel', '7766554433', 'redbull@example.com');

INSERT INTO sponsors_event (sponsorID, eventID, amount)
VALUES
(1, 1, 50000),
(2, 2, 120000),
(3, 3, 80000);

INSERT INTO Staff (name, role, phone_no, email, salary)
VALUES
('Amit Verma', 'Security', '9123456789', 'amit.security@example.com', 25000),
('Sneha Nair', 'Technician', '9234567890', 'sneha.tech@example.com', 30000),
('Rahul Joshi', 'Manager', '9345678901', 'rahul.manager@example.com', 45000),
('Deepa Rao', 'Volunteer', '9456789012', 'deepa.volunteer@example.com', 15000);

INSERT INTO works_at (staffID, eventID, shift)
VALUES
(1, 1, 'EVENING'),
(2, 2, 'FULL_DAY'),
(3, 3, 'MORNING'),
(4, 4, 'FULL_DAY');

-- FUNCTIONS 

-- Function 1: Calculate total revenue for an event
DELIMITER //
CREATE FUNCTION Get_Event_Revenue(event_id INT)
RETURNS DECIMAL(10,2)
DETERMINISTIC
READS SQL DATA
BEGIN
    DECLARE total_rev DECIMAL(10,2);
    
    SELECT COALESCE(SUM(t.price), 0) INTO total_rev
    FROM Ticket t
    WHERE t.eventID = event_id AND t.status = 'SOLD';
    
    RETURN total_rev;
END //
DELIMITER ;

-- Function 2: Get total tickets sold for an event
DELIMITER //
CREATE FUNCTION Get_Tickets_Sold_Count(event_id INT)
RETURNS INT
DETERMINISTIC
READS SQL DATA
BEGIN
    DECLARE sold_count INT;
    
    SELECT COUNT(*) INTO sold_count
    FROM Ticket
    WHERE eventID = event_id AND status = 'SOLD';
    
    RETURN sold_count;
END //
DELIMITER ;

-- Function 3: Get available tickets count for an event
DELIMITER //
CREATE FUNCTION Get_Available_Tickets_Count(event_id INT)
RETURNS INT
DETERMINISTIC
READS SQL DATA
BEGIN
    DECLARE avail_count INT;
    
    SELECT COUNT(*) INTO avail_count
    FROM Ticket
    WHERE eventID = event_id AND status = 'AVAILABLE';
    
    RETURN avail_count;
END //
DELIMITER ;

-- Function 4: Calculate occupancy percentage for an event
DELIMITER //
CREATE FUNCTION Get_Event_Occupancy_Percentage(event_id INT)
RETURNS DECIMAL(5,2)
DETERMINISTIC
READS SQL DATA
BEGIN
    DECLARE occupancy DECIMAL(5,2);
    DECLARE attendee_count INT;
    DECLARE venue_cap INT;
    
    SELECT COUNT(DISTINCT a.attendeeID) INTO attendee_count
    FROM attends a
    WHERE a.eventID = event_id;
    
    SELECT v.capacity INTO venue_cap
    FROM Events e
    JOIN Venue v ON e.venueID = v.venueID
    WHERE e.eventID = event_id;
    
    IF venue_cap > 0 THEN
        SET occupancy = (attendee_count * 100.0) / venue_cap;
    ELSE
        SET occupancy = 0;
    END IF;
    
    RETURN occupancy;
END //
DELIMITER ;

-- Function 5: Get total sponsorship amount for an event
DELIMITER //
CREATE FUNCTION Get_Total_Sponsorship(event_id INT)
RETURNS DECIMAL(10,2)
DETERMINISTIC
READS SQL DATA
BEGIN
    DECLARE total_sponsor DECIMAL(10,2);
    
    SELECT COALESCE(SUM(amount), 0) INTO total_sponsor
    FROM sponsors_event
    WHERE eventID = event_id;
    
    RETURN total_sponsor;
END //
DELIMITER ;

-- Function 6: Get total artist fees for an event
DELIMITER //
CREATE FUNCTION Get_Total_Artist_Fees(event_id INT)
RETURNS DECIMAL(10,2)
DETERMINISTIC
READS SQL DATA
BEGIN
    DECLARE total_fees DECIMAL(10,2);
    
    SELECT COALESCE(SUM(ar.fee), 0) INTO total_fees
    FROM performs p
    JOIN Artist ar ON p.artistID = ar.artistID
    WHERE p.eventID = event_id;
    
    RETURN total_fees;
END //
DELIMITER ;

-- Function 7: Get net profit for an event
DELIMITER //
CREATE FUNCTION Get_Event_Net_Profit(event_id INT)
RETURNS DECIMAL(10,2)
DETERMINISTIC
READS SQL DATA
BEGIN
    DECLARE net_profit DECIMAL(10,2);
    DECLARE total_revenue DECIMAL(10,2);
    DECLARE total_expenses DECIMAL(10,2);
    DECLARE venue_cost DECIMAL(10,2);
    DECLARE artist_fees DECIMAL(10,2);
    DECLARE staff_cost DECIMAL(10,2);
    
    -- Get revenue
    SELECT COALESCE(SUM(t.price), 0) INTO total_revenue
    FROM Ticket t
    WHERE t.eventID = event_id AND t.status = 'SOLD';
    
    -- Add sponsorship
    SELECT total_revenue + COALESCE(SUM(se.amount), 0) INTO total_revenue
    FROM sponsors_event se
    WHERE se.eventID = event_id;
    
    -- Get venue cost
    SELECT v.cost INTO venue_cost
    FROM Events e
    JOIN Venue v ON e.venueID = v.venueID
    WHERE e.eventID = event_id;
    
    -- Get artist fees
    SELECT COALESCE(SUM(ar.fee), 0) INTO artist_fees
    FROM performs p
    JOIN Artist ar ON p.artistID = ar.artistID
    WHERE p.eventID = event_id;
    
    -- Get staff cost
    SELECT COALESCE(SUM(s.salary), 0) INTO staff_cost
    FROM works_at wa
    JOIN Staff s ON wa.staffID = s.staffID
    WHERE wa.eventID = event_id;
    
    SET total_expenses = venue_cost + artist_fees + staff_cost;
    SET net_profit = total_revenue - total_expenses;
    
    RETURN net_profit;
END //
DELIMITER ;

-- Function 8: Check if venue is available for a date/time
DELIMITER //
CREATE FUNCTION Is_Venue_Available(
    venue_id INT,
    event_date DATE,
    start_time TIME,
    end_time TIME
)
RETURNS BOOLEAN
DETERMINISTIC
READS SQL DATA
BEGIN
    DECLARE clash_count INT;
    
    SELECT COUNT(*) INTO clash_count
    FROM Events
    WHERE venueID = venue_id
    AND date = event_date
    AND status != 'Cancelled'
    AND (
        (start_time >= Events.start_time AND start_time < Events.end_time)
        OR
        (end_time > Events.start_time AND end_time <= Events.end_time)
        OR
        (start_time <= Events.start_time AND end_time >= Events.end_time)
    );
    
    RETURN clash_count = 0;
END //
DELIMITER ;

-- Function 9: Get attendee count for an event
DELIMITER //
CREATE FUNCTION Get_Attendee_Count(event_id INT)
RETURNS INT
DETERMINISTIC
READS SQL DATA
BEGIN
    DECLARE att_count INT;
    
    SELECT COUNT(DISTINCT attendeeID) INTO att_count
    FROM attends
    WHERE eventID = event_id;
    
    RETURN att_count;
END //
DELIMITER ;

-- Function 10: Get artist count for an event
DELIMITER //
CREATE FUNCTION Get_Artist_Count(event_id INT)
RETURNS INT
DETERMINISTIC
READS SQL DATA
BEGIN
    DECLARE art_count INT;
    
    SELECT COUNT(DISTINCT artistID) INTO art_count
    FROM performs
    WHERE eventID = event_id;
    
    RETURN art_count;
END //
DELIMITER ;

-- STORED PROCEDURES 

-- 1. Calculate Event Revenue (Using Function)
DELIMITER //
CREATE PROCEDURE Calculate_Event_Revenue(IN event_id INT)
BEGIN
    SELECT 
        e.eventID,
        e.name AS event_name,
        Get_Event_Revenue(event_id) AS total_revenue,
        Get_Tickets_Sold_Count(event_id) AS tickets_sold
    FROM Events e
    WHERE e.eventID = event_id;
END //
DELIMITER ;

-- 2. Get Event Statistics (Using Functions)
DELIMITER //
CREATE PROCEDURE Get_Event_Statistics(IN event_id INT)
BEGIN
    SELECT 
        e.eventID,
        e.name AS event_name,
        e.date,
        e.status,
        v.name AS venue_name,
        v.capacity AS venue_capacity,
        Get_Attendee_Count(event_id) AS total_attendees,
        Get_Artist_Count(event_id) AS total_artists,
        COUNT(DISTINCT s.staffID) AS total_staff,
        COUNT(DISTINCT sp.sponsorID) AS total_sponsors,
        Get_Total_Sponsorship(event_id) AS total_sponsorship,
        Get_Tickets_Sold_Count(event_id) AS tickets_sold,
        (SELECT COUNT(*) FROM Ticket WHERE eventID = event_id) AS total_tickets,
        Get_Event_Revenue(event_id) AS total_revenue,
        Get_Event_Net_Profit(event_id) AS net_profit
    FROM Events e
    LEFT JOIN Venue v ON e.venueID = v.venueID
    LEFT JOIN works_at wa ON e.eventID = wa.eventID
    LEFT JOIN Staff s ON wa.staffID = s.staffID
    LEFT JOIN sponsors_event se ON e.eventID = se.eventID
    LEFT JOIN Sponsor sp ON se.sponsorID = sp.sponsorID
    WHERE e.eventID = event_id
    GROUP BY e.eventID, e.name, e.date, e.status, v.name, v.capacity;
END //
DELIMITER ;

-- 3. Auto Assign Default Staff
DELIMITER //
CREATE PROCEDURE Auto_Assign_Default_Staff(IN event_id INT)
BEGIN
    DECLARE staff_count INT;
    
    -- Check if staff already assigned
    SELECT COUNT(*) INTO staff_count
    FROM works_at
    WHERE eventID = event_id;
    
    -- If no staff assigned, add default staff
    IF staff_count = 0 THEN
        -- Assign one staff member from each role (if available)
        INSERT INTO works_at (staffID, eventID, shift)
        SELECT staffID, event_id, 'FULL_DAY'
        FROM Staff
        WHERE role IN ('Security', 'Manager')
        LIMIT 2;
        
        SELECT CONCAT('Default staff assigned to event ', event_id) AS message;
    ELSE
        SELECT CONCAT('Staff already assigned to event ', event_id) AS message;
    END IF;
END //
DELIMITER ;

-- REPORT PROCEDURES (Using Functions Above)

-- Report 1: Events with Venue Capacity & Tickets Sold
DELIMITER //
CREATE PROCEDURE Report_Events_Venue_Tickets()
BEGIN
    SELECT 
        e.eventID,
        e.name AS event_name,
        e.date,
        e.status,
        v.name AS venue_name,
        v.type AS venue_type,
        v.capacity AS venue_capacity,
        (SELECT COUNT(*) FROM Ticket WHERE eventID = e.eventID) AS total_tickets,
        Get_Tickets_Sold_Count(e.eventID) AS tickets_sold,
        Get_Available_Tickets_Count(e.eventID) AS tickets_available,
        Get_Event_Revenue(e.eventID) AS revenue
    FROM Events e
    JOIN Venue v ON e.venueID = v.venueID
    ORDER BY e.date;
END //
DELIMITER ;

-- Report 2: Top 3 Most Attended Events
DELIMITER //
CREATE PROCEDURE Report_Top_Attended_Events()
BEGIN
    SELECT 
        e.eventID,
        e.name AS event_name,
        e.date,
        Get_Attendee_Count(e.eventID) AS total_attendees,
        v.capacity,
        Get_Event_Occupancy_Percentage(e.eventID) AS attendance_rate
    FROM Events e
    JOIN Venue v ON e.venueID = v.venueID
    ORDER BY total_attendees DESC
    LIMIT 3;
END //
DELIMITER ;

-- Report 3: Sponsors & Contribution per Event
DELIMITER //
CREATE PROCEDURE Report_Sponsor_Contributions()
BEGIN
    SELECT 
        e.eventID,
        e.name AS event_name,
        s.sponsorID,
        s.name AS sponsor_name,
        s.industry,
        se.amount AS contribution_amount
    FROM Events e
    JOIN sponsors_event se ON e.eventID = se.eventID
    JOIN Sponsor s ON se.sponsorID = s.sponsorID
    ORDER BY e.eventID, se.amount DESC;
END //
DELIMITER ;

-- Report 4: Artist Performance Count Per Event
DELIMITER //
CREATE PROCEDURE Report_Artist_Performances()
BEGIN
    SELECT 
        e.eventID,
        e.name AS event_name,
        Get_Artist_Count(e.eventID) AS artist_count,
        GROUP_CONCAT(ar.name SEPARATOR ', ') AS artist_names,
        SUM(p.noOfSongs) AS total_songs,
        Get_Total_Artist_Fees(e.eventID) AS total_artist_fees
    FROM Events e
    LEFT JOIN performs p ON e.eventID = p.eventID
    LEFT JOIN Artist ar ON p.artistID = ar.artistID
    GROUP BY e.eventID, e.name
    ORDER BY artist_count DESC;
END //
DELIMITER ;

-- Report 5: Attendee Demographics (Age/Gender Breakdown)
DELIMITER //
CREATE PROCEDURE Report_Attendee_Demographics()
BEGIN
    SELECT 
        gender,
        CASE 
            WHEN age BETWEEN 5 AND 17 THEN 'Minor (5-17)'
            WHEN age BETWEEN 18 AND 25 THEN 'Youth (18-25)'
            WHEN age BETWEEN 26 AND 40 THEN 'Adult (26-40)'
            WHEN age BETWEEN 41 AND 60 THEN 'Middle Age (41-60)'
            ELSE 'Senior (60+)'
        END AS age_group,
        COUNT(*) AS count,
        ROUND(AVG(age), 1) AS avg_age
    FROM Attendee
    GROUP BY gender, age_group
    ORDER BY gender, age_group;
END //
DELIMITER ;

-- QUERY FUNCTIONS 

-- Query 1: JOIN - Events with Venue Name & Total Tickets Sold
DELIMITER //
CREATE PROCEDURE Query_Events_With_Venue_Details()
BEGIN
    SELECT 
        e.eventID,
        e.name AS event_name,
        e.date,
        v.name AS venue_name,
        v.capacity,
        COUNT(t.ticketID) AS total_tickets,
        COUNT(CASE WHEN t.status = 'SOLD' THEN 1 END) AS tickets_sold,
        ROUND((COUNT(CASE WHEN t.status = 'SOLD' THEN 1 END) * 100.0 / v.capacity), 2) AS occupancy_percentage
    FROM Events e
    JOIN Venue v ON e.venueID = v.venueID
    LEFT JOIN Ticket t ON e.eventID = t.eventID
    GROUP BY e.eventID, e.name, e.date, v.name, v.capacity
    ORDER BY e.date;
END //
DELIMITER ;

-- Query 2: AGGREGATE - Total Revenue per Venue & Event
DELIMITER //
CREATE PROCEDURE Query_Revenue_Per_Venue()
BEGIN
    SELECT 
        v.venueID,
        v.name AS venue_name,
        COUNT(DISTINCT e.eventID) AS total_events,
        COALESCE(SUM(CASE WHEN t.status = 'SOLD' THEN t.price ELSE 0 END), 0) AS total_revenue,
        COALESCE(AVG(CASE WHEN t.status = 'SOLD' THEN t.price END), 0) AS avg_ticket_price
    FROM Venue v
    LEFT JOIN Events e ON v.venueID = e.venueID
    LEFT JOIN Ticket t ON e.eventID = t.eventID
    GROUP BY v.venueID, v.name
    ORDER BY total_revenue DESC;
END //
DELIMITER ;

-- UTILITY PROCEDURES FOR PYTHON INTEGRATION

-- Get all events with full details
DELIMITER //
CREATE PROCEDURE Get_All_Events()
BEGIN
    SELECT 
        e.*,
        v.name AS venue_name,
        v.address,
        v.capacity
    FROM Events e
    JOIN Venue v ON e.venueID = v.venueID
    ORDER BY e.date DESC;
END //
DELIMITER ;

-- Get tickets for a specific event
DELIMITER //
CREATE PROCEDURE Get_Event_Tickets(IN event_id INT)
BEGIN
    SELECT 
        t.*,
        e.name AS event_name,
        CASE WHEN p.attendeeID IS NOT NULL THEN a.name ELSE 'Not Purchased' END AS purchased_by
    FROM Ticket t
    JOIN Events e ON t.eventID = e.eventID
    LEFT JOIN purchases p ON t.ticketID = p.ticketID
    LEFT JOIN Attendee a ON p.attendeeID = a.attendeeID
    WHERE t.eventID = event_id
    ORDER BY t.type, t.seatNo;
END //
DELIMITER ;

-- Get artists performing at an event
DELIMITER //
CREATE PROCEDURE Get_Event_Artists(IN event_id INT)
BEGIN
    SELECT 
        ar.*,
        p.noOfSongs,
        e.name AS event_name
    FROM Artist ar
    JOIN performs p ON ar.artistID = p.artistID
    JOIN Events e ON p.eventID = e.eventID
    WHERE e.eventID = event_id
    ORDER BY ar.name;
END //
DELIMITER ;

-- Get staff assigned to an event
DELIMITER //
CREATE PROCEDURE Get_Event_Staff(IN event_id INT)
BEGIN
    SELECT 
        s.*,
        wa.shift,
        e.name AS event_name
    FROM Staff s
    JOIN works_at wa ON s.staffID = wa.staffID
    JOIN Events e ON wa.eventID = e.eventID
    WHERE e.eventID = event_id
    ORDER BY s.role, s.name;
END //
DELIMITER ;

-- Get sponsors for an event
DELIMITER //
CREATE PROCEDURE Get_Event_Sponsors(IN event_id INT)
BEGIN
    SELECT 
        s.*,
        se.amount,
        e.name AS event_name
    FROM Sponsor s
    JOIN sponsors_event se ON s.sponsorID = se.sponsorID
    JOIN Events e ON se.eventID = e.eventID
    WHERE e.eventID = event_id
    ORDER BY se.amount DESC;
END //
DELIMITER ;

-- Get attendees for an event
DELIMITER //
CREATE PROCEDURE Get_Event_Attendees(IN event_id INT)
BEGIN
    SELECT 
        a.*,
        e.name AS event_name
    FROM Attendee a
    JOIN attends att ON a.attendeeID = att.attendeeID
    JOIN Events e ON att.eventID = e.eventID
    WHERE e.eventID = event_id
    ORDER BY a.name;
END //
DELIMITER ;

-- Get all venues
DELIMITER //
CREATE PROCEDURE Get_All_Venues()
BEGIN
    SELECT * FROM Venue ORDER BY name;
END //
DELIMITER ;

-- Get all artists
DELIMITER //
CREATE PROCEDURE Get_All_Artists()
BEGIN
    SELECT * FROM Artist ORDER BY name;
END //
DELIMITER ;

-- Get all staff
DELIMITER //
CREATE PROCEDURE Get_All_Staff()
BEGIN
    SELECT * FROM Staff ORDER BY role, name;
END //
DELIMITER ;

-- Get all sponsors
DELIMITER //
CREATE PROCEDURE Get_All_Sponsors()
BEGIN
    SELECT * FROM Sponsor ORDER BY name;
END //
DELIMITER ;

-- Get all attendees
DELIMITER //
CREATE PROCEDURE Get_All_Attendees()
BEGIN
    SELECT * FROM Attendee ORDER BY name;
END //
DELIMITER ;

-- Get event financial summary (Using Functions)
DELIMITER //
CREATE PROCEDURE Get_Event_Financial_Summary(IN event_id INT)
BEGIN
    SELECT 
        e.eventID,
        e.name AS event_name,
        e.budget,
        v.cost AS venue_cost,
        Get_Event_Revenue(event_id) AS ticket_revenue,
        Get_Total_Sponsorship(event_id) AS sponsorship_revenue,
        Get_Total_Artist_Fees(event_id) AS artist_expenses,
        COALESCE(SUM(s.salary), 0) AS staff_expenses,
        (Get_Event_Revenue(event_id) + Get_Total_Sponsorship(event_id)) AS total_revenue,
        (v.cost + Get_Total_Artist_Fees(event_id) + COALESCE(SUM(s.salary), 0)) AS total_expenses,
        Get_Event_Net_Profit(event_id) AS net_profit
    FROM Events e
    JOIN Venue v ON e.venueID = v.venueID
    LEFT JOIN works_at wa ON e.eventID = wa.eventID
    LEFT JOIN Staff s ON wa.staffID = s.staffID
    WHERE e.eventID = event_id
    GROUP BY e.eventID, e.name, e.budget, v.cost;
END //
DELIMITER ;

-- VIEWS 

-- View: Complete Event Summary
CREATE VIEW view_event_summary AS
SELECT 
    e.eventID,
    e.name AS event_name,
    e.date,
    e.status,
    e.start_time,
    e.end_time,
    v.name AS venue_name,
    v.capacity,
    COUNT(DISTINCT t.ticketID) AS total_tickets,
    COUNT(DISTINCT CASE WHEN t.status = 'SOLD' THEN t.ticketID END) AS sold_tickets,
    COUNT(DISTINCT att.attendeeID) AS registered_attendees,
    COUNT(DISTINCT p.artistID) AS artist_count,
    COUNT(DISTINCT wa.staffID) AS staff_count,
    COUNT(DISTINCT se.sponsorID) AS sponsor_count
FROM Events e
JOIN Venue v ON e.venueID = v.venueID
LEFT JOIN Ticket t ON e.eventID = t.eventID
LEFT JOIN attends att ON e.eventID = att.eventID
LEFT JOIN performs p ON e.eventID = p.eventID
LEFT JOIN works_at wa ON e.eventID = wa.eventID
LEFT JOIN sponsors_event se ON e.eventID = se.eventID
GROUP BY e.eventID, e.name, e.date, e.status, e.start_time, e.end_time, v.name, v.capacity;

-- View: Available Tickets
CREATE VIEW view_available_tickets AS
SELECT 
    t.ticketID,
    t.type,
    t.price,
    t.seatNo,
    e.eventID,
    e.name AS event_name,
    e.date AS event_date,
    v.name AS venue_name
FROM Ticket t
JOIN Events e ON t.eventID = e.eventID
JOIN Venue v ON e.venueID = v.venueID
WHERE t.status = 'AVAILABLE'
ORDER BY e.date, t.type, t.price;


