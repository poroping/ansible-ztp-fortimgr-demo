import subprocess, json
from flask import Flask, render_template, url_for, flash, redirect
from data import fake_data
from forms import AddDeviceForm

app = Flask(__name__)
app.config['SECRET_KEY'] = '5736b7a8b78f231916bf3eeab6fc55aa'

@app.route('/', methods=['GET', 'POST'])
@app.route('/adddevice', methods=['GET', 'POST'])
def adddevice():
    form = AddDeviceForm()
    if form.validate_on_submit():
        playbook = "../05_true_zero_touch.yml"
        inventory = "../inventory"
        args = {
            "customerid": form.customer.data,
            "serial": form.serial.data,
            "line": form.line.data
        }
        ansible_proc = subprocess.Popen(['ansible-playbook', playbook, '-i',
            inventory, '-e', json.dumps(args)], shell=False,
             bufsize=1)
        if ansible_proc.poll() is not None and ansible_proc.returncode != 0:
            flash('Error running subprocess', 'danger')
            return redirect(url_for('adddevice'))
        flash(f'{form.serial.data} staging commencing.', 'success')
        return redirect(url_for('adddevice'))
    return render_template('adddevice.html', title='Add device', form=form)



@app.route('/json', methods=['GET'])
def rtnjson():
    return fake_data

if __name__ == '__main__':
   app.run(debug=True, host='0.0.0.0')
