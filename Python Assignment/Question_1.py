def generate_invites(guest_list, event_details):
    BORDER = '*' * 50
    INNER_WIDTH = 46

    def make_line(text=''): # use a auxillary function to create each line of the card, centering the text and truncating if its too long and/or empty.
        if len(text) > INNER_WIDTH:
            text = text[:INNER_WIDTH - 3] + '...'
        return f"* {text.center(INNER_WIDTH)} *"

    def build_card(guest):
        lines = [
            BORDER,
            make_line("Saraswati Puja Invitation"),
            make_line("Utkal Parishad, IIT Kanpur"),
            make_line(),
            make_line(f"Dear {guest['Name']},"),
            make_line(guest['Affiliation']),
            make_line(),
            make_line(f"Date: {event_details['Date']}"),
            make_line(f"Venue: {event_details['Venue']}"),
            make_line(f"Schedule: {event_details['Schedule']}"),
            BORDER,
        ]
        return '\n'.join(lines)

    return {guest['Email']: build_card(guest) for guest in guest_list}

#put your input here

guests = [
    {'Name': 'Aman', 'Affiliation': 'CSE Dept', 'Email': 'aman@iitk.ac.in'},
    {'Name': 'Dr. Very Long Name That Definitely Exceeds The Character Limit',
     'Affiliation': 'Physics Dept', 'Email': 'dr.long@iitk.ac.in'}
]
details = {'Date': 'Feb 14, 2026', 'Venue': 'Community Hall', 'Schedule': '10:00 AM'}

invites = generate_invites(guests, details)
for email, card in invites.items():
    print(f"To: {email}\n{card}\n")