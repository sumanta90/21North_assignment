from flask import Flask, render_template, request, flash
from flask_wtf import FlaskForm
from flaskext.mysql import MySQL
from werkzeug.security import generate_password_hash
from werkzeug.utils import redirect
from wtforms import StringField, SubmitField, DecimalField
from wtforms.validators import InputRequired, DataRequired
import time
from flask import escape

mysql = MySQL()
app = Flask(__name__)

app.config['SECRET_KEY'] = "mysecretkey"

app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'Sumanta12345@'
app.config['MYSQL_DATABASE_DB'] = 'assignment'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'

mysql.init_app(app)

class NewQueueForm(FlaskForm):
    ambid = StringField("Ambassador ID", validators=[InputRequired("Field is required!"), DataRequired("Data is required!")])
    queueid = StringField("Queue Id", validators=[InputRequired("Queue is required!"), DataRequired("Queue is required!")])
    amount = DecimalField("Amount", validators=[InputRequired("Amount is required!"), DataRequired("Amount is required!")])
    taskcount = StringField("Task Count")
    state = StringField("State Code")
    reason = StringField("Enter reason")
    submit = SubmitField("Submit")


@app.route("/")
def index():
    return render_template('index.html')


@app.route("/queue/add")
def add_queue():
    #form = NewQueueForm()
    return render_template('add_queue.html')


@app.route("/process/queue/add", methods=['POST'])
def process_queue_add():
    ambid = request.form.get('ambid')
    queue = request.form.get('queue')
    amount = request.form.get("amount")
    tcount = request.form.get("tcount")
    state = request.form.get("state")
    reason = request.form.get("reason")

    if len(reason) < 2:
        reason = "NULL"

    #validation start
    if not ambid.isdecimal() or int(ambid)<=0:
        flash('Ambassador id should be a decimal number')
        return redirect("/queue/add")
    if not queue.isdecimal():
        flash('Queue id should be a decimal number')
        return redirect("/queue/add")
    if not amount.isdecimal():
        flash('Amount should be a decimal number')
        return redirect("/queue/add")
    if not tcount.isdecimal():
        flash('Task count be a decimal number')
        return redirect("/queue/add")
    if not state.isdecimal():
        flash('Amount should be a decimal number')
        return redirect("/queue/add")


    #validation end

    try:
            dt = time.strftime('%Y-%m-%d %H:%M:%S')
            sql = "INSERT INTO queue(ambid, queueid, mmount, taskcount, state, reason, dt) VALUES( % s, % s, % s, % s, % s, % s, % s)"
            data = (ambid, queue, amount, tcount, state, reason, dt)
            conn = mysql.connect()
            cursor = conn.cursor()

            cursor.execute("select * from queue where ambid='" + ambid + "' and queueid='" + queue + "'")
            rows = cursor.fetchall()
            if cursor.rowcount:
                flash('Combination of same Amb.id and Queue id already exist!')
                return redirect("/queue/add")
            else:
                cursor.execute(sql, data)
                conn.commit()
                flash('User added successfully!')
                return redirect("/queue/add")
    except Exception as ex:
        flash('Something error occured, can not add data!')
        return redirect("/queue/add")
    finally:
        cursor.close()
        conn.close()

@app.route("/queue/list")
def list_queue():
    conn = None
    cursor = None
    try:
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute("select * from queue")
        rows = cursor.fetchall()
        return render_template('queue_list.html', table=rows)
    except Exception as e:
        flash("Problem in fetching..")
        return redirect("/queue/list")
    finally:
        cursor.close()
        conn.close()
    #return render_template('queue_list.html')


@app.route('/delete/<int:idd>')
def delete_user(idd):
    conn = None
    cursor = None
    try:
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute("delete from queue where id='%s'", idd)
        conn.commit()
        flash('User deleted successfully!')
        return redirect('/queue/list')
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()



@app.route("/process/delete", methods=['POST'])
def delete():
    conn = None
    cursor = None
    try:
        ambid = request.form.get("ambid")
        queue = request.form.get("queue")

        conn = mysql.connect()
        cursor = conn.cursor()
        sql = "delete FROM queue where ambid='"+ambid+"' and queueid='"+queue+"'"

        cursor.execute("select * from queue where ambid='"+ambid+"' and queueid='"+queue+"'")
        rows = cursor.fetchall()
        if cursor.rowcount:
            cursor.execute(sql)
            conn.commit()
            flash('User deleted!')
            return redirect('/queue/delete')
        else:
            flash("No row found with these information!")
            return redirect("/queue/delete")

    except Exception as e:
        print(e)
        flash('Problem in delete.')
        return redirect('/queue/delete')
    finally:
        cursor.close()
        conn.close()


@app.route("/queue/delete")
def delete_queue():
    return render_template('delete_queue.html')



@app.route("/edit/<int:id>")
def editLoad(id):
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("select * from queue where id='" + str(id) + "'")
    rows = cursor.fetchone()
    return render_template("edit.html", data=rows)


@app.route("/process/update/<int:idd>", methods=['POST'])
def processsUpdate(idd):
    ambid = request.form.get('ambid')
    queue = request.form.get('queue')
    amount = request.form.get("amount")
    tcount = request.form.get("tcount")
    state = request.form.get("state")
    reason = request.form.get("reason")


    ls = [idd,ambid,queue,amount,tcount,state,reason]
    print(ls)
    conn = None
    cursor = None
    try:
        sql = "update queue SET ambid=%s, queueid=%s, mmount=%s, taskcount=%s, state=%s, reason=%s where id = %s"
        data = (ambid, queue, amount, tcount, state,reason, idd)
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute(sql, data)
        conn.commit()
        flash('Queue updated successfully!')
        return redirect('/queue/list')
    except Exception as e:
        print(e)
        flash('Problem with update')
        return redirect('/queue/list')
    finally:
        cursor.close()
        conn.close()


if __name__ == '__main__':
    app.run('127.0.0.1', 5000, True)
