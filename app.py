from flask import Flask, g, request, jsonify
from database import get_db
from functools import wraps

app = Flask(__name__)

api_username = 'admin'
api_password = '1234'

def protected(f):
	@wraps(f)
	def decorated(*args, **kwargs):
		auth = request.authorization
		if auth and auth.username == api_username and auth.password == api_password:
			return f(*args, **kwargs)
		return jsonify(message='Authentication failed'), 403
	return decorated



# Required to close the database connection after every request
@app.teardown_appcontext
def close_db(error):
	if hasattr(g, 'sqlite_db'):
		g.sqlite_db.close()


@app.route('/member', methods=['GET'])
#@protected
def get_members():

	db = get_db()
	members_cur = db.execute('select * from members')
	members_results = members_cur.fetchall()
	
	members = [{'id':member['id'], 'name':member['name'], 'email':member['email'], 'level':member['level']} for member in members_results]

	return jsonify(members=members)
	
	

@app.route('/member/<int:member_id>', methods=['GET'])
#@protected
def get_member(member_id):

	db = get_db()
	members_cur = db.execute('select * from members where id = ?', [member_id])
	member_result = members_cur.fetchone()
	
	member ={'id':member_result['id'], 'name':member_result['name'], 'email':member_result['email'], 'level':member_result['level']}

	return jsonify(member=member)

@app.route('/member', methods=['POST'])
def add_member():
	new_member_data = request.get_json()

	name = new_member_data['name']
	email = new_member_data['email']
	level = new_member_data['level']

	db = get_db()
	# Here i am using a cursor to get the last row id
	cursor=db.cursor()
	cursor.execute('insert into members (name, email, level) values (?, ?, ?)', [name, email, level])
	db.commit()

	# Get the row inserted previously so it can be returned as a response
	member_cur = db.execute('select * from members where id = ?', [cursor.lastrowid])
	member_result = member_cur.fetchone()
	
	member ={'id':member_result['id'], 'name':member_result['name'], 'email':member_result['email'], 'level':member_result['level']}

	return jsonify(member=member)


@app.route('/member/<int:member_id>', methods=['PUT', 'PATCH'])
def edit_member(member_id):

	new_member_data = request.get_json()
	print(new_member_data)

	name = new_member_data['name']
	email = new_member_data['email']
	level = new_member_data['level']
	
	db = get_db()
	db.execute('update members set name = ?, email = ?, level = ? where id = ?', [name, email, level, member_id])
	db.commit()

	
	# Get the row updated previously so it can be returned as a response
	member_cur = db.execute('select * from members where id = ?', [member_id])
	member_result = member_cur.fetchone()
	
	member ={'id':member_result['id'], 'name':member_result['name'], 'email':member_result['email'], 'level':member_result['level']}

	return jsonify(member=member)
	
	#return 'This updates a member by ID'

@app.route('/member/<int:member_id>', methods=['DELETE'])
def delete_member(member_id):

	db = get_db()
	db.execute('delete from members where id = ?', [member_id])
	db.commit()
	return jsonify(message='The member been deleted')


if __name__ == '__main__':
	app.run(debug=True)