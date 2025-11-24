def register_routes(app):
    from .auth import auth_bp
    from .admin import admin_bp
    from .user import user_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(user_bp, url_prefix='/api/user')
    
    print('[ROUTES] ✓ Registered: auth, admin, user')
