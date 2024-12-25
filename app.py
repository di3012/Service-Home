# main.py
from flask import render_template, request, redirect, url_for, flash, jsonify
from app import db, create_app
from app.models import User, Service, ServiceRequest, Category, Professional
from app.utils import hash_password, verify_password, login_user, logout_user, require_role
from flask_login import LoginManager, login_user, current_user, login_required
from datetime import datetime
from sqlalchemy import and_
# from  import db

app = create_app()


# Flask-Login Setup
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    user_id = int(user_id)
    return User.query.filter_by(id=user_id).first()

# Routes

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register_customer():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = hash_password(request.form.get('password'))
        address = request.form.get('address')
        pin_code = request.form.get('pin_code')
        contact_no = request.form.get('contact_no')

        if not email or not password:
            flash("Email and password are required.", "error")
            return render_template('registration_customer.html')
        if not address:
            flash("Address is required.", "error")
            return render_template('registration_customer.html')
        if not pin_code:
            flash("Pin code is required.", "error")
            return render_template('registration_customer.html')
        
        # Save the new user
        new_user = User(name=name, email=email, password=password, role='customer', address= address, pin_code= pin_code, contact_no= contact_no)
        db.session.add(new_user)
        db.session.commit()
        flash("Registration successful! Please log in.", "success")
        return redirect(url_for('login'))

    return render_template('registration_customer.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()

        if user and verify_password(user.password, password):
            login_user(user)
            if user.role == 'customer':
                return redirect(url_for('customer_dashboard'))
            if user.role == 'professional':
                return redirect(url_for('professional_dashboard'))
            if user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            # return redirect(url_for('some_other_dashboard'))
        
        flash("Invalid credentials", "error")
    return render_template('login.html')

@app.route('/customer/dashboard')
@login_required
@require_role('customer')
def customer_dashboard():
    categories = Category.query.all()
    services_by_category = {}

    services_list = Service.query.all()
    professional_list = Professional.query.all()
        
    services_by_category = {category.id: category.services for category in categories}

    # Fetch service history for the logged-in customer
    service_history = ServiceRequest.query.filter_by(customer_id=current_user.id).all()
    completed_request_list = []
    current_request_list = []
    for request in service_history:
        service = Service.query.filter_by(id=request.service_id).first()
        professional = Professional.query.filter_by(id=request.professional_id).first()
        if not request.status == 'completed':
            current_request_list.append({
                'service' : service.name,
                'professional' : professional.name,
                'date_of_request' : request.date_of_request,
                'professional_phone' : professional.contact_no,
                'status' : request.status,
                'id' : request.id
            })
        elif request.status == 'completed':
             completed_request_list.append({
            'service': service.name,
            'professional': professional.name,
            'date_of_request': request.date_of_request,
            'professional_id' : request.professional_id,
            'rate' : request.rate,
            'service_id' : request.service_id
            })
    
       
        

    return render_template(
        'customer_dashboard.html',
        customer=current_user,
        categories=categories,
        services_list=services_list,
        services_by_category=services_by_category,
        completed_request_list=completed_request_list,
        professional_list=professional_list,
        current_request_list=current_request_list
    )

@app.route('/book_service', methods=['POST'])
@login_required
@require_role('customer')
def book_service(): 

    service_id = request.form.get('service_id')
    professional_id = request.form.get('professional_id')
    date_of_request = request.form.get('date_of_request')  # Fetch the selected date
    
    professional_data = Professional.query.filter_by(id=professional_id).first()
    service = Service.query.filter_by(professional_email=professional_data.email).first()
    service_id = service.id

    if not service_id:
        if professional_id:
            professional_data = Professional.query.filter_by(id=professional_id).first()
            service = Service.query.filter_by(professional_email=professional_data.email).first()
            service_id = service.id
        else:
            return jsonify({'error': 'Service ID is required'}), 400
    
    
    if not date_of_request:
        return jsonify({'error': 'Date of request is required'}), 400

    # Convert date_of_request to datetime
    try:
        date_of_request = datetime.strptime(date_of_request, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Invalid date format'}), 400

    # Fetch the service details
    service = Service.query.filter_by(id=service_id).first()
    if not service:
        return jsonify({'error': 'Service not found'}), 404

    # Fetch the professional if provided
    professional = Professional.query.filter_by(id=professional_id).first() if professional_id else None

    # Create a new service request
    new_request = ServiceRequest(
        customer_id=current_user.id,
        service_id=service_id,
        professional_id=professional.id if professional else None,
        location=current_user.address,  # Assuming customer's address is the location
        pin_code=current_user.pin_code,
        date_of_request=date_of_request,
        status='requested',
        remarks='New service request created.'
    )

    # Add to the database
    db.session.add(new_request)
    db.session.commit()

    # Redirect to dashboard or return JSON
    return jsonify({'success': 'Service booked successfully', 'request_id': new_request.id}), 200

@app.route('/customer/service_request', methods=['POST'])
@login_required
@require_role('customer')
def customer_service_request():
    
    service_id = request.form.get('service_id')

    action = request.form.get('action')
    service = ServiceRequest.query.filter_by(id=service_id).first()
    # professional = Professional.query.filter_by(id=current_user.id).first()
    
    if action == 'complete':
        service.status = "completed"
        db.session.commit() 
        flash("Service request completed.", "success")

    elif action == 'cancel':
        service.status = "cancelled"
        db.session.commit()
        flash("Service request cancelled.", "success")

    return redirect(url_for('customer_dashboard'))

@app.route('/customer/profile', methods=['GET', 'POST'])
@login_required
@require_role('customer')
def customer_profile():
    customer_id= current_user.id
    customer = User.query.filter_by(id=customer_id).first()


    if request.method == 'POST':
        customer.name = request.form.get('name')
        customer.email = request.form.get('email')
        customer.address = request.form.get('address')
        customer.pin_code = request.form.get('pin_code')
        customer.contact_no = request.form.get('contact_no')
        

        # Validate changes and commit
        try:
            db.session.commit()
            flash('Profile updated successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating profile: {str(e)}', 'danger')

        return redirect(url_for('customer_profile'))

    return render_template('customer_profile.html', customer=customer)

@app.route('/customer/search', methods=['GET', 'POST'])
@login_required
@require_role('customer')
def customer_search():
   
    if request.method == 'POST':
        service_name = request.form.get('service_name')
        city = request.form.get('city')
        category = request.form.get('category')

        
        # Ensure at least one search parameter is filled
        if not (service_name or city or category):
            service_list = Professional.query.all()
        else: 
            query = db.session.query(Professional)    
        
            if service_name:
                service_list = query.filter(Professional.service.ilike(f"%{service_name}%"))
            if city:
                service_list = query.filter(Professional.city.ilike(f"%{city}%"))
            if category:
                service_list = query.filter(Professional.category.ilike(f"%{category}%"))

            if service_name and city:
                service_list = query.filter(and_(Professional.service.ilike(f"%{service_name}%"), Professional.city.ilike(f"%{city}%"))).all()
            if service_name and category:
                service_list = query.filter(and_(Professional.service.ilike(f"%{service_name}%"), Professional.category.ilike(f"%{category}%"))).all()
            if city and category:
                service_list = query.filter(and_(Professional.city.ilike(f"%{city}%"), Professional.category.ilike(f"%{category}%"))).all()
            if service_name and city and category:
                service_list = query.filter(and_(Professional.service.ilike(f"%{service_name}%"), Professional.city.ilike(f"%{city}%"), Professional.category.ilike(f"%{category}%"))).all()

        return render_template('customer_search.html', service_list=service_list)
    
    return render_template('customer_search.html')


@app.route('/customer/summary')
@login_required
@require_role('customer')
def customer_summary():

    customer_id = current_user.id

    service_completed, service_accepted, service_rejected, service_cancelled, service_requested = 0, 0, 0, 0, 0

    service_request = ServiceRequest.query.filter_by(customer_id=customer_id).all()

    for request in service_request:
        if request.status == 'completed':
            service_completed += 1
        elif request.status == 'accepted':
            service_accepted += 1
        elif request.status == 'rejected':
            service_rejected += 1
        elif request.status == 'cancelled':
            service_cancelled += 1
        elif request.status == 'requested':
            service_requested += 1

    service_count = [service_requested, service_accepted, service_completed, service_rejected, service_cancelled  ]   
            
    return render_template('customer_summary.html', service_count=service_count)

@app.route('/admin/dashboard')
@login_required
@require_role('admin')
def admin_dashboard():
    if current_user.role != 'admin':
        flash("You do not have permission to access this page.", "warning")
        return redirect(url_for('home'))  # Redirects non-admin users to the home page
    services = Service.query.all()
    categories = Category.query.all()
    pending_professionals = Professional.query.filter_by(approved=False).all()
    approved_professionals = Professional.query.filter_by(approved=True).all()

    service_requests = ServiceRequest.query.all()
    return render_template('admin_dashboard.html', services=services,
                           categories=categories, pending_professionals=pending_professionals,
        approved_professionals=approved_professionals, service_requests=service_requests)


@app.route('/admin/add_service', methods=['POST'])
@login_required
@require_role('admin')
def add_service():
    name = request.form.get('name')
    category_id = request.form.get('category_id')
    category_detail = Category.query.filter_by(id=category_id).first()
    if category_detail:
        category = category_detail.name
    else:
        category = None
    base_price = request.form.get('base_price')
    professional = request.form.get('professional')
    professional_email = request.form.get('email')
    city = request.form.get('city')
    contact_no = request.form.get('contact_no')
    pin_code = request.form.get('pin_code')
    expireance = request.form.get('expireance')

    if not name:
        flash("Service name is required.", "error")
        return redirect(url_for('admin_dashboard'))

    if not category_id:
        flash("Category is required.", "error")
        return redirect(url_for('admin_dashboard'))
    
    if not base_price:
        flash("Base price is required.", "error")
        return redirect(url_for('admin_dashboard'))

    # Convert base_price to a float and handle any errors
    try:
        base_price = float(base_price)
    except ValueError:
        flash("Base price must be a number.", "error")
        return redirect(url_for('admin_dashboard'))
    new_professional = Professional(name=professional, email=professional_email, city=city, contact_no=contact_no, pin_code=pin_code, expireance=expireance,
                                    approved=True, password = hash_password('pwd123'), service = name, category = category, role='professional', base_price=base_price)
    new_service = Service(name=name, category_id=category_id, base_price=base_price, professional_email=professional_email)
    new_user = User(email=professional_email, password=hash_password('pwd123'), name=professional, role='professional', address=city, pin_code=pin_code, contact_no=contact_no)
    db.session.add(new_professional)
    db.session.add(new_user)
    db.session.add(new_service)
    db.session.commit()
    flash('Service added successfully!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/add_category', methods=['POST'])
@login_required
@require_role('admin')
def add_category():
    name = request.form.get('category_name')

    if not name:
        flash("Category name is required.", "error")
        return redirect(url_for('admin_dashboard'))
    

    # Ensure category name is unique
    if Category.query.filter_by(name=name).first():
        flash("Category already exists.", "error")
        return redirect(url_for('admin_dashboard'))

    new_category = Category(name=name)
    db.session.add(new_category)
    db.session.commit()
    flash('Category added successfully!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/manage_professional', methods=['POST'])
@login_required
@require_role('admin')
def manage_professional():
    if current_user.role != 'admin':
        flash("You do not have permission to perform this action.", "warning")
        return redirect(url_for('home'))

    professional_id = request.form.get('professional_id')
    action = request.form.get('action')
    professional = Professional.query.filter_by(id=professional_id).first()
    professional_email = professional.email
    category = professional.category
    category_detail = Category.query.filter_by(name=category).first()

    if category_detail:
        category_id = category_detail.id
    else:
        category = None

    service = professional.service
    rate = professional.rate
    base = professional.base_price

    new_service = Service(name=service, category_id=category_id, base_price=base, professional_email=professional_email, rate=rate)

    if action == 'approve':
        professional.approved = True
        db.session.add(new_service)
        db.session.commit()
        flash(f"{professional.name} approved.", "success")
    elif action == 'reject':

        db.session.delete(professional)
        db.session.commit()
        flash(f"{professional.name} rejected.", "info")

    return redirect(url_for('admin_dashboard'))

@app.route('/admin/professional/edit/<int:professional_id>', methods=['GET', 'POST'])
@login_required
@require_role('admin')
def edit_professional(professional_id):
    professional = Professional.query.filter_by(id=professional_id).first()

    service = Service.query.filter_by(professional_email=professional.email).first()

    if request.method == 'POST':
        # Update professional's details
        professional.contact_no = request.form.get('contact_no')
        professional.city = request.form.get('city')
        professional.pin_code = request.form.get('pin_code')
        professional.expireance = request.form.get('expireance')
        professional.people = request.form.get('people')
        professional.base_price = request.form.get('base_price')

        service.base_price = request.form.get('base_price')
        service.professional.contact_no = request.form.get('contact_no')
        service.professional.city = request.form.get('city')
        service.professional.pin_code = request.form.get('pin_code')
        service.professional.expireance = request.form.get('expireance')
        service.professional.people = request.form.get('people')

        # Validate changes and commit
        try:
            db.session.commit()
            flash('Profile updated successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating profile: {str(e)}', 'danger')

        
        flash("Professional details updated successfully.", "success")
        return redirect(url_for('admin_dashboard'))
    
    return render_template('edit_professional.html', professional=professional)

@app.route('/admin/professional/delete/<int:professional_id>', methods=['POST'])
@login_required
@require_role('admin')
def delete_professional(professional_id):
    professional = Professional.query.filter_by(id=professional_id).first()
    user = User.query.filter_by(email=professional.email).first()
    service = Service.query.filter_by(professional_email=professional.email).first()
    db.session.delete(professional)
    db.session.delete(user)
    db.session.delete(service)
    db.session.commit()
    flash("Professional deleted successfully.", "info")
    return redirect(url_for('admin_dashboard'))


@app.route('/admin/service/edit/<int:service_id>', methods=['GET','POST'])
@login_required
@require_role('admin')
def edit_service(service_id):
    service = Service.query.filter_by(id=service_id).first()
    professional_email = service.professional_email
    professional = Professional.query.filter_by(email=professional_email).first()
    # category = Category.query.filter_by(id=service.category_id).first()
    # category_name = category.name

    if request.method == 'POST':
        # Update professional's details
        service.name = request.form.get('name')
        # service.category_id = request.form.get('category_id')
        service.base_price = request.form.get('base_price')

        professional.service = request.form.get('name')
        # professional.category = category_name
        professional.base_price = request.form.get('base_price')
        # Validate changes and commit
        try:
            db.session.commit()
            flash('Profile updated successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating profile: {str(e)}', 'danger')

        
        flash("Professional details updated successfully.", "success")
        return redirect(url_for('admin_dashboard'))
    
    return render_template('edit_service.html', service=service)

@app.route('/admin/delete_service/<int:service_id>', methods=['POST'])
@login_required
@require_role('admin')
def delete_service(service_id):
    service = Service.query.filter_by(id=service_id).first()
    user = User.query.filter_by(email=service.professional_email).first()
    professional = Professional.query.filter_by(email=service.professional_email).first()
    db.session.delete(user)
    db.session.delete(service)
    db.session.delete(professional)
    db.session.commit()
    flash('Service deleted successfully!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/search', methods=['GET', 'POST'])
@login_required
@require_role('admin')
def admin_search():
    
    if request.method == 'POST':
        service_name = request.form.get('service_name')
        professional_name = request.form.get('professional_name')
        customer_name = request.form.get('customer_name')

        # Ensure at least one search parameter is filled
        if (service_name and professional_name or professional_name):
            flash('choose one filed please', 'danger')
            return redirect(url_for('admin_search'))    
        else: 
            query_service = db.session.query(Service)  
            query_professional = db.session.query(Professional)
            query_customer = db.session.query(User)

            if service_name:
                service_list = query_service.filter(Service.name.ilike(f"%{service_name}%"))
                professional_list = []
                customer_list = []
            if professional_name:
                professional_list = query_professional.filter(Professional.name.ilike(f"%{professional_name}%"))
                service_list = []
                customer_list = []
            if customer_name:
                customer_list = query_customer.filter(User.name.ilike(f"%{customer_name}%"))
                service_list = []
                professional_list = []

            # if service_name and professional_name:
            #     flash('choose one filed', 'danger')
            #     return redirect(url_for('admin_search'))
            # if service_name and customer_name:
            #     flash('choose one filed', 'danger')
            #     return redirect(url_for('admin_search'))
            # if professional_name and customer_name:
            #     flash('choose one filed', 'danger')
            #     return redirect(url_for('admin_search'))
            # if service_name and professional_name and customer_name:
            #     flash('choose one filed', 'danger')

        return render_template('admin_search.html', service_list=service_list, professional_list=professional_list, customer_list=customer_list)
    
    return render_template('admin_search.html')

@app.route('/admin/summary')
@login_required
@require_role('admin')
def admin_summary():

    service_completed, service_accepted, service_rejected, service_cancelled, service_requested = 0, 0, 0, 0, 0
    customer, professional =  0, 0

    service_request = ServiceRequest.query.all()
    users_list = User.query.all()

    for request in service_request:
        if request.status == 'completed':
            service_completed += 1
        elif request.status == 'accepted':
            service_accepted += 1
        elif request.status == 'rejected':
            service_rejected += 1
        elif request.status == 'cancelled':
            service_cancelled += 1
        elif request.status == 'requested':
            service_requested += 1
    
    for user in users_list:
        if user.role == 'customer':
            customer += 1
        elif user.role == 'professional':
            professional += 1

    service_count = [service_requested, service_accepted, service_completed, service_rejected, service_cancelled  ] 
    users_count = [customer, professional]  


    return render_template('admin_summary.html', service_count=service_count, users_count = users_count)      

@app.route('/register_professional', methods=['GET', 'POST'])
def register_professional():

    category = Category.query.all()

    if request.method == 'POST':
        # Collect form data
        name = request.form.get('name')
        email = request.form.get('email')
        password = hash_password(request.form.get('password'))
        pin_code = request.form.get('pin_code')
        contact_no = request.form.get('contact_no')
        city = request.form.get('city')
        service = request.form.get('service')
        people = request.form.get('no_of_people')
        expireance = request.form.get('experience')
        category_name = request.form.get('category_name')
        base_price = request.form.get('base_price')
        role = 'professional'
        # Validate and check for duplicates

        if not name:
            flash("Name is required.", "error")
            return render_template('registration_professional.html')

        if not email:
            flash("Email is required.", "error")
            return render_template('registration_professional.html')

        if not password:
            flash("Password is required.", "error")
            return render_template('registration_professional.html')

        if not service:
            flash("Service is required.", "error")
            return render_template('registration_professional.html')
        
        if not contact_no or not pin_code:
            flash("Contact no and Pin Code are required.", "error")
            return render_template('registration_professional.html')
        

        # Check if email already exists
        existing_professional = Professional.query.filter_by(email=email).first()
        if existing_professional:
            flash("An account with this email already exists.", "error")
            return render_template('registration_professional.html')

        # Create a new Professional entry with `approved=False`
        new_professional = Professional( 
            name=name,
            email=email,
            password=password,
            pin_code=pin_code,
            contact_no=contact_no,
            city=city,
            service=service,
            people= people,
            expireance=expireance,
            category=category_name,
            base_price=base_price,
            approved=False,  # Mark as pending approval
            role=role
            )
        new_user = User(name=name, email=email, password=password, role=role, address=city, pin_code=pin_code, contact_no=contact_no)
        db.session.add(new_user)
        db.session.add(new_professional)
        db.session.commit()

        flash("Your registration is pending admin approval.", "info")
        return redirect(url_for('login'))

    return render_template('registeration_professional.html', category=category)

@app.route('/professional/dashboard')
@login_required
@require_role('professional')
def professional_dashboard():
    prof_email= current_user.email
    professional = Professional.query.filter_by(email=prof_email).first()
    pending_request = []
    current_request = []
    completed_request = []
    cancelled_request = []

    if not professional.approved:
      flash("The admin is yet to approve your account. It takes between 20 to 40 hours for the process to be done. Please wait until then.", "info")
    else:
        
        service_request = ServiceRequest.query.filter_by(professional_id=professional.id).all()
        for request in service_request:
            user = User.query.filter_by(id=request.customer_id).first()
            if request.status == 'requested':
                pending_request.append({
                    'id' : request.id,
                    'customer_name' : user.name,
                    'customer_address' : user.address,
                    'customer_pin_code' : user.pin_code,
                    'customer_contact_no' : user.contact_no,
                    'date_of_request' : request.date_of_request
                })
            elif request.status == 'accepted':
                current_request.append({
                    'id' : request.id,
                    'customer_name' : user.name,
                    'customer_address' : user.address,
                    'customer_pin_code' : user.pin_code,
                    'customer_contact_no' : user.contact_no,
                    'date_of_request' : request.date_of_request
                })
            elif request.status == 'completed':
                completed_request.append({
                    'id' : request.id,
                    'customer_name' : user.name,
                    'customer_address' : user.address,
                    'customer_pin_code' : user.pin_code,
                    'customer_contact_no' : user.contact_no,
                    'date_of_request' : request.date_of_request,
                    'rate' : request.rate
                })
            elif request.status == 'cancelled' or request.status == 'rejected':
                cancelled_request.append({
                    'id' : request.id,
                    'customer_name' : user.name,
                    'customer_address' : user.address,
                    'customer_pin_code' : user.pin_code,
                    'customer_contact_no' : user.contact_no,
                    'date_of_request' : request.date_of_request,
                    'status' : request.status
                })



    return render_template('professional_dashboard.html', professional=professional, pending_request=pending_request, 
                           current_request=current_request, completed_request=completed_request, cancelled_request=cancelled_request)

@app.route('/professional/service_request', methods=['POST'])
@login_required
@require_role('professional')
def professional_service_request():
    
    service_id = request.form.get('service_id')
    print(f"Received service_id: {service_id}")  # Debugging line

    action = request.form.get('action')
    service = ServiceRequest.query.filter_by(id=service_id).first()
    # professional = Professional.query.filter_by(id=current_user.id).first()


    if action == 'accept':
        service.status = "accepted"
        db.session.commit()
        flash("Service request accepted.", "success")

    elif action == 'reject':
        service.status = "Rejected"
        db.session.commit()
        flash("Service request rejected.", "success")

    elif action == 'complete':
        service.status = "completed"
        db.session.commit() 
        flash("Service request completed.", "success")

    elif action == 'cancel':
        service.status = "cancelled"
        db.session.commit()
        flash("Service request cancelled.", "success")

    return redirect(url_for('professional_dashboard'))

@app.route('/rate_professional', methods=['POST'])
@login_required
@require_role('customer')
def rate_professional():
    professional_id = request.form.get('professional_id')
    rating = request.form.get('rating')
    service_id = request.form.get('service_id')

    if not professional_id or not rating:
        return jsonify({'success': False, 'error': 'Invalid input'})

    try:
        # Convert rating to float
        rating = float(rating)

        # Fetch the professional from the database
        professional = Professional.query.filter_by(id=professional_id).first()
        service = ServiceRequest.query.filter_by(service_id=service_id).first()
        if not professional.rate == 0.0:
            rate_already = professional.rate
            rate = (rate_already + rating)/2
        else:
            rate = rating
        if not professional:
            return jsonify({'success': False, 'error': 'Professional not found'})

        # Update the professional's rate
        service.rate = rate
        professional.rate = rate
        db.session.commit()

        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
    
@app.route('/professional/profile', methods=['GET', 'POST'])
@login_required
@require_role('professional')
def professional_profile():
    prof_email= current_user.email
    professional = Professional.query.filter_by(email=prof_email).first()
    service = Service.query.filter_by(professional_email=professional.email).first()
    # category = Category.query.filter_by(id=professional.category).first()

    if request.method == 'POST':
        # Update professional's details
        professional.name = request.form.get('name')
        professional.email = request.form.get('email')
        professional.contact_no = request.form.get('contact_no')
        professional.city = request.form.get('city')
        # professional.category = request.form.get('category')
        professional.pin_code = request.form.get('pin_code')
        professional.expireance = request.form.get('expireance')
        professional.people = request.form.get('people')
        professional.base_price = request.form.get('base_price')

        service.base_price = request.form.get('base_price')
        service.professional_email = request.form.get('email')
        service.professional.name = request.form.get('name')
        service.professional.contact_no = request.form.get('contact_no')
        service.professional.city = request.form.get('city')
        service.professional.pin_code = request.form.get('pin_code')
        service.professional.expireance = request.form.get('expireance')
        service.professional.people = request.form.get('people')

        # Validate changes and commit
        try:
            db.session.commit()
            flash('Profile updated successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating profile: {str(e)}', 'danger')

        return redirect(url_for('professional_profile'))

    return render_template('professional_profile.html', professional=professional)

@app.route('/professional/summary')
@login_required
@require_role('professional')
def professional_summary():

    professional = Professional.query.filter_by(email=current_user.email).first()
    professional_id = professional.id
    service_completed, service_accepted, service_rejected, service_cancelled, service_requested = 0, 0, 0, 0, 0

    service_request = ServiceRequest.query.filter_by(professional_id=professional_id).all()

    for request in service_request:
        if request.status == 'completed':
            service_completed += 1
        elif request.status == 'accepted':
            service_accepted += 1
        elif request.status == 'rejected':
            service_rejected += 1
        elif request.status == 'cancelled':
            service_cancelled += 1
        elif request.status == 'requested':
            service_requested += 1

    service_count = [service_requested, service_accepted, service_completed, service_rejected, service_cancelled  ]   
    return render_template('professional_summary.html', service_count=service_count)

def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == '__main__':
    # with app.app_context():
    #     db.create_all()  # Create tables
    app.run(debug=True)