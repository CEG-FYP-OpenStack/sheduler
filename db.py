import MySQLdb

db = MySQLdb.connect(host="127.0.0.1",user="root",passwd="password",db="nova")

cursor = db.cursor()
cursor.execute("select memory_mb_used from compute_nodes")

data = cursor.fetchone()

print "Ram used: %s" % data

cursor.execute("select vcpus_used,vcpus from compute_nodes")

data = cursor.fetchall()

for row in data:
	cpu_used = row[0]
	cpu = row[1]
	print "Cpu_used: %s, Cpu: %s" % (cpu_used,cpu)

db.close()
