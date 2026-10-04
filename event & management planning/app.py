from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

DATABASE = "event.db"


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def create_tables():
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            location TEXT NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            description TEXT NOT NULL
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS registrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            FOREIGN KEY(event_id) REFERENCES events(id)
        )
    """)

    # Add sample events only if table is empty
    count = conn.execute("SELECT COUNT(*) FROM events").fetchone()[0]

    if count == 0:
        sample_events = [
            (
                "College Tech Fest",
                "Technology",
                "Chennai",
                "2026-10-20",
                "10:00 AM",
                "A technical event with coding competitions, workshops and project exhibitions."
            ),
            (
                "Cultural Fest",
                "Cultural",
                "Bangalore",
                "2026-11-05",
                "5:00 PM",
                "A cultural celebration featuring music, dance and entertainment."
            ),
            (
                "Business Conference",
                "Business",
                "Hyderabad",
                "2026-11-15",
                "9:30 AM",
                "A conference for students and professionals interested in entrepreneurship."
            )
        ]

        conn.executemany("""
            INSERT INTO events
            (name, category, location, date, time, description)
            VALUES (?, ?, ?, ?, ?, ?)
        """, sample_events)

    conn.commit()
    conn.close()


@app.route("/")
def home():
    conn = get_db()
    events = conn.execute(
        "SELECT * FROM events ORDER BY date LIMIT 3"
    ).fetchall()
    conn.close()

    return render_template("index.html", events=events)


@app.route("/events")
def events():
    search = request.args.get("search", "")

    conn = get_db()

    if search:
        events = conn.execute("""
            SELECT * FROM events
            WHERE name LIKE ?
               OR category LIKE ?
               OR location LIKE ?
        """, (
            "%" + search + "%",
            "%" + search + "%",
            "%" + search + "%"
        )).fetchall()
    else:
        events = conn.execute(
            "SELECT * FROM events ORDER BY date"
        ).fetchall()

    conn.close()

    return render_template(
        "events.html",
        events=events,
        search=search
    )


@app.route("/event/<int:event_id>")
def event_details(event_id):
    conn = get_db()

    event = conn.execute(
        "SELECT * FROM events WHERE id = ?",
        (event_id,)
    ).fetchone()

    conn.close()

    if event is None:
        return "Event not found"

    return render_template(
        "details.html",
        event=event
    )


@app.route("/add-event", methods=["GET", "POST"])
def add_event():
    if request.method == "POST":

        name = request.form["name"]
        category = request.form["category"]
        location = request.form["location"]
        date = request.form["date"]
        time = request.form["time"]
        description = request.form["description"]

        conn = get_db()

        conn.execute("""
            INSERT INTO events
            (name, category, location, date, time, description)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            name,
            category,
            location,
            date,
            time,
            description
        ))

        conn.commit()
        conn.close()

        return redirect(url_for("events"))

    return render_template("add_event.html")


@app.route("/register/<int:event_id>", methods=["GET", "POST"])
def register(event_id):

    conn = get_db()

    event = conn.execute(
        "SELECT * FROM events WHERE id = ?",
        (event_id,)
    ).fetchone()

    conn.close()

    if event is None:
        return "Event not found"

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        phone = request.form["phone"]

        conn = get_db()

        conn.execute("""
            INSERT INTO registrations
            (event_id, name, email, phone)
            VALUES (?, ?, ?, ?)
        """, (
            event_id,
            name,
            email,
            phone
        ))

        conn.commit()
        conn.close()

        return redirect(url_for(
            "event_details",
            event_id=event_id
        ))

    return render_template(
        "register.html",
        event=event
    )


@app.route("/admin")
def admin():

    conn = get_db()

    registrations = conn.execute("""
        SELECT
            registrations.id,
            registrations.name,
            registrations.email,
            registrations.phone,
            events.name AS event_name,
            events.date AS event_date
        FROM registrations
        JOIN events
        ON registrations.event_id = events.id
        ORDER BY registrations.id DESC
    """).fetchall()

    conn.close()

    return render_template(
        "admin.html",
        registrations=registrations
    )


if __name__ == "__main__":
    create_tables()
    app.run(debug=True)