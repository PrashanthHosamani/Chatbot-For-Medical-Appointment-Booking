from flask import Flask, render_template, send_from_directory
import os
from app import app as application

app = application

if __name__ == '__main__':
    app.run()