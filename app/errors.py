from flask import render_template

from app import app, db


@app.errorhandler(404)
def not_found_error(error):
    app.logger.error('404 not found')
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    app.logger.error('Internal error, please wait until the maintainers fix the issue')
    db.session.rollback()
    return render_template('errors/500.html'),500