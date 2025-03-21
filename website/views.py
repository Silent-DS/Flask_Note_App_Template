from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from .models import Note
from . import db
import json

views = Blueprint('views', __name__)

@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    # Check if the method is POST, which is when the user adds a note
    if request.method == 'POST':
        note = request.form.get('note')  # Get the note content from the form

        if len(note) < 1:
            flash('Note is too short!', category='error')  # Display error if note is empty
        else:
            new_note = Note(data=note, user_id=current_user.id)  # Create a new note
            db.session.add(new_note)  # Add note to the session
            db.session.commit()  # Commit to the database
            flash('Note added!', category='success')  # Show success message

    # Get the search query from the URL parameters (if any)
    search_query = request.args.get('search', '')

    # If there is a search query, filter notes based on the search text
    if search_query:
        notes = Note.query.filter(Note.data.ilike(f'%{search_query}%'), Note.user_id == current_user.id).all()
    else:
        # Otherwise, fetch all notes from the current user
        notes = Note.query.filter_by(user_id=current_user.id).all()

    return render_template("home.html", user=current_user, notes=notes, search_query=search_query)


@views.route('/delete-note', methods=['POST'])
def delete_note():
    # Get the note id from the request
    note = json.loads(request.data)
    noteId = note['noteId']
    
    # Find the note by its id
    note = Note.query.get(noteId)
    if note:
        # Make sure the note belongs to the current user
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()

    return jsonify({})
