from PIL import Image
from flask import url_for, current_app
from flask_mail import Message
from cicksblog import mail
import secrets
import os


def save_pict(form_pict):
    # generate random string
    rand_hex = secrets.token_hex(8)
    # split name of file and extension
    _, file_ext = os.path.splitext(form_pict.filename)
    # create new file name
    file_name = rand_hex + file_ext
    # path where file will be saved
    file_path = os.path.join(current_app.root_path, "static/img", file_name)
    # resize the image
    img = Image.open(form_pict)
    img.thumbnail((250, 250))
    # save picture
    img.save(file_path)
    # return picture name
    return file_name


def send_token_email(user):
    token = user.get_token()
    message = Message(
        subject="[Password Reset Request | Cicks Blog]",
        sender="example@gmail.com",
        recipients=[user.email],
    )
    message.html = f"""
        <h1> Hello, {user.email}. </h1>
        <p> To reset your password, please visit the following link: </p>
        <p> {url_for('users.reset_password', token=token, _external=True)} </p>
        <p> Don't worry, your data will not be lost. </p>
        <small> Link will be expire in 30 minutes. </small>
    """
    mail.send(message)