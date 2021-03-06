from flask import Blueprint, render_template, flash, request, redirect, url_for
from flask_login import current_user, login_required, login_user, logout_user
from flask_babel import gettext

from maediprojects.query import user as quser
from maediprojects.query import organisations as qorganisations
from maediprojects.lib import codelists
from maediprojects.views.api import jsonify
from maediprojects.extensions import login_manager


blueprint = Blueprint('users', __name__, url_prefix='/', static_folder='../static')


@login_manager.user_loader
def load_user(id):
    return quser.user(id)


@blueprint.route("/profile/", methods=["GET", "POST"])
@login_required
def profile():
    if current_user.administrator:
        return redirect(url_for("users.users_edit", user_id=current_user.id))

    if request.method == "POST":
        data = {
            k: v
            for k, v in request.form.items()
            if k in ["name", "organisation", "recipient_country_code",
                     "change_password", "password"]
        }
        data["id"] = current_user.id
        data["username"] = current_user.username
        data["email_address"] = current_user.email_address

        if quser.updateUser(data):
            flash(gettext(u"Profile successfully updated!"), "success")
        else:
            flash(gettext(u"Sorry, couldn't update!"), "danger")
        return redirect(url_for("users.profile"))

    return render_template("profile.html",
                           codelists=codelists.get_codelists(),
                           user=current_user,
                           loggedinuser=current_user)


@blueprint.route("/users/")
@login_required
@quser.administrator_required
def users():
    if not current_user.administrator:
        flash(gettext(u"You must be an administrator to access that area."), "danger")
    users = quser.user()
    return render_template("users.html",
                           users=users,
                           loggedinuser=current_user)


@blueprint.route("/users/delete/", methods=["POST"])
@login_required
@quser.administrator_required
def users_delete():
    if not current_user.administrator:
        flash(gettext(u"You must be an administrator to create new users."), "danger")
        return redirect(url_for("activities.dashboard"))
    if current_user.username == request.form.get("username"):
        flash(gettext(u"You cannot delete your own user."), "danger")
        return redirect(url_for("activities.dashboard"))
    if quser.deleteUser(request.form.get('username')):
        flash(gettext(u"Successfully deleted user."), "success")
    else:
        flash(gettext(u"Sorry, there was an error and that user could not be deleted."), "danger")
    return redirect(url_for("users.users"))


@blueprint.route("/users/new/", methods=["GET", "POST"])
@login_required
@quser.administrator_required
def users_new():
    #if not current_user.administrator:
    #    flash("You must be an administrator to create new users.", "danger")
    #    return redirect(url_for("activities.dashboard"))
    if request.method == "GET":
        user = {
            "permissions_dict": {
                "domestic_external": current_user.permissions_dict["domestic_external"]
            },
            "recipient_country_code": "LR"
        }
        return render_template("user.html",
                               user=user,
                               loggedinuser=current_user,
                               codelists=codelists.get_codelists())
    elif request.method == "POST":
        user = quser.addUser(request.form)
        if user:
            flash(gettext(u"Successfully created user!"), "success")
            return redirect(url_for("users.users_edit", user_id=user.id))
        else:
            flash(gettext(u"Sorry, couldn't create that user!"), "danger")
        return redirect(url_for("users.users"))


@blueprint.route("/users/<user_id>/", methods=["GET", "POST"])
@login_required
@quser.administrator_required
def users_edit(user_id):
    if not current_user.administrator:
        flash("You must be an administrator to edit users.", "danger")
        return redirect(url_for("activities.dashboard"))
    if request.method == "GET":
        user = quser.user(user_id)
        return render_template("user.html",
                 user=user,
                 loggedinuser=current_user,
                 organisations=qorganisations.get_organisations(),
                 codelists=codelists.get_codelists())
    elif request.method == "POST":
        data = request.form.to_dict()
        data["id"] = user_id
        if quser.updateUser(data):
            flash(gettext(u"Successfully updated user!"), "success")
        else:
            flash(gettext(u"Sorry, couldn't update that user!"), "danger")
        return redirect(url_for("users.users_edit", user_id=user_id))


@blueprint.route("/users/<user_id>/permissions/", methods=["GET", "POST"])
@login_required
@quser.administrator_required
def user_permissions_edit(user_id):
    def _append_organisation(uo, organisations):
        uo["organisations"] = dict(map(lambda o: (o.id, o.as_dict()), organisations))
        if uo["organisations"].get(uo["organisation_id"]):
            uo["organisations"].get(uo["organisation_id"])["selected"] = " selected"
        uo["organisations"] = list(uo["organisations"].values())
        select_options = {True: " selected", False: ""}
        uo["permission_values"] = [
            {"name": "View projects", "value": "view", "selected": select_options[bool(uo["permission_value"] == "view")]},
            {"name": "Edit projects", "value": "edit", "selected": select_options[bool(uo["permission_value"] == "edit")]}
        ]
        return uo

    if not current_user.administrator:
        flash("You must be an administrator to edit users.", "danger")
        return redirect(url_for("activities.dashboard"))
    if request.method == "GET":
        user = quser.user(user_id)
        user_organisations = list(map(lambda uo:
            (_append_organisation(uo.as_dict(), qorganisations.get_organisations())),
            user.organisations))
        return jsonify(permissions=user_organisations)
    elif request.method == "POST":
        data = request.form.to_dict()
        data["user_id"] = user_id
        if data["action"] == "add":
            op = quser.addOrganisationPermission(data)
            if not op: return "False"
            return jsonify({
                "id": op.id,
                "organisations": list(map(lambda o: o.as_dict(),
                    qorganisations.get_organisations())),
              "permission_values": [
                {
                  "selected": " selected",
                  "name": "View projects",
                  "value": "view"
                },
                {
                  "selected": "",
                  "name": "Edit projects",
                  "value": "edit"
                }
              ],
                })
        elif data["action"] == "delete":
            op = quser.deleteOrganisationPermission(data)
            if not op:
                return False
            return "ok"
        elif data["action"] == "edit":
            op = quser.updateOrganisationPermission(data)
            if not op:
                return False
            return "ok"
        return "error, unknown action"


@blueprint.route("/login/", methods=["GET", "POST"])
def login():
    if request.method == "POST" and "username" in request.form:
        user = quser.user_by_username(request.form["username"])
        if (user and user.check_password(request.form["password"])):
            if login_user(user):
                flash(gettext(u"Logged in!"), "success")
                if request.args.get("next"):
                    redir_url = request.script_root + request.args.get("next")
                else:
                    redir_url = url_for("activities.dashboard")
                return redirect(redir_url)
            else:
                flash(gettext(u"Sorry, but you could not log in."), "danger")
        else:
            flash(gettext(u"Invalid username or password."), "danger")
    return render_template("login.html",
             loggedinuser=current_user)

@blueprint.route('/logout/')
@login_required
def logout():
    logout_user()
    flash(gettext(u'Logged out'), 'success')
    redir_url = url_for("users.login")
    return redirect(redir_url)
