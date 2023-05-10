from datetime import datetime


class Message:
    def __init__(
        self, text: str, sender: str, sent_at: datetime, message_id: int
    ):
        self.text = text
        self.sender = sender
        self.sent_at = sent_at
        self.id = message_id

    def __str__(self):
        return f"sent by {self.sender} at {self.sent_at.isoformat()}\n{self.text}"
