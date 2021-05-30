from app import db


# Ассоциативная таблица пользователей и событий (many-to-many).
users_to_events = db.Table(
    "users_to_events",
    db.Column("user_name", db.String(64), db.ForeignKey("users.username")),
    db.Column("event_name", db.String(64), db.ForeignKey("events.name"))
)


class UserModel(db.Model):
    __tablename__ = "users"

    username = db.Column(db.String(64), primary_key=True, index=True)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(64))


class EventModel(db.Model):
    __tablename__ = "events"

    name = db.Column(db.String(64), primary_key=True, index=True)
    organizer = db.Column(db.String(64), index=True)
    type_game = db.Column(db.String(64))
    mode_game = db.Column(db.String(64))
    current_count_users = db.Column(db.Integer)
    max_count_users = db.Column(db.Integer)
    run_date = db.Column(db.DateTime, index=True)
    duration = db.Column(db.Time)
    record_avail = db.Column(db.Boolean)
    broadcast_avail = db.Column(db.Boolean)
    users = db.relationship("UserModel",
                            secondary=users_to_events,
                            backref=db.backref("events", lazy="dynamic"),
                            lazy="dynamic")
