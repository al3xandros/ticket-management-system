from flask import *
import database
import dataclasses

import forms
import settings


db = database.DB()

app = Flask(__name__)
app.secret_key = b'b1cbe80f9b569a93da92abcb441283cab282'

@app.route("/")
def index():
    links = [i for i in forms.Form.forms.keys()]
    return render_template("index.html", site_map=links)


@app.route("/<classname>/", methods=["GET", "POST"])
def default_router(classname):
    results = dict()
    form_class = forms.Form.forms.get(classname)
    if form_class is None:
        return abort(404)

    form_class.prefetch_data()

    if request.method == 'POST':
        form = form_class(**dict(request.form.items()))

        results = form.execute(db)

        for msg in form.get_success_messages():
            flash(msg, "success")

        for msg in form.get_failure_messages():
            flash(msg, "failure")

        # return redirect(f"/{classname}/")

    return render_template("base_form.html",
                           input_fields=form_class.to_form(),
                           results=results,
                           page_title=classname,
                           enum=enumerate)

@app.route("/_dummy/")
def create_dummy():
    import db_create_fake_data
    return redirect("/")


if __name__ == "__main__":
    app.run(
        host=settings.HTTP_HOST,
        port=settings.HTTP_PORT,
        debug=settings.DEBUG
    )

