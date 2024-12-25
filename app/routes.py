# app/routes.py
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from .models import User, Service, ServiceRequest  # Use relative import
from . import db  # Import db from app.__init__.py
