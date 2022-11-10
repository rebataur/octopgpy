from flask import Flask,render_template,request,jsonify
import json


# import psycopg2

# conn = psycopg2.connect(
#         host="localhost",
#         database="postgres",
#         user="postgres",
#         password="postgres"
# )

# Open a cursor to perform database operations

import sqlite3





app = Flask(__name__)

@app.route('/')
def hello(name=None):
    return render_template('hello.html', name="dfdfdf")

@app.route('/jsontosql',methods=['POST'])
def jsontosql():
    print(request.get_json())
    jsonsql = request.get_json()
    sql = jsontosql(jsonsql)
    conn = sqlite3.connect('C:\\3Projects\\newstockup\\stockup.db')
    cur = conn.cursor()
    cur.execute(sql)
    res = cur.fetchall()
    # print(res)
    jsonres = (json.dumps(res))
    print(jsonres)
    return json.dumps({'success':True,'sql':sql,'res':jsonres}), 200, {'ContentType':'application/json'} 

def jsontosql(jsonsql):
    ctes = [jsonsql]
    sql = ''
    i = 0
    for cte in ctes:

        if i == 0:
            sql += f"with {cte['name']} as( select  "
        else:
            sql += f", {cte['name']} as ( select  "

        columns = []
        c = ""
        for col in cte['cols']:
            print(col)
            print(col['type'])
            col_type = col['type']
            if col_type == "normal":
                columns.append(col['name'])
            elif col_type == 'window_function':
                attribs = col['attributes']
                # print(attribs)
                # print("-------s")
                closing_braces = ""
                # if attribs['round'] == 'true':
                #     c += f"ROUND("
                #     closing_braces += ")"
                c += f" {attribs['window_func']}("
                closing_braces += ")"
                c += f"{attribs['col']}"
                c += closing_braces

                c += " over("
                over = attribs['over']
                # print(over)

                order_by = over['order_by']
                order_type = over['order_type']

                c += f" order by {order_by} {order_type} " if len(
                    order_by) > 0 else ''

                frame_spec = over['frame_spec']

                if frame_spec['type'] == 'rows':
                    c += 'rows'
                if over['partition_by'] != '':
                    c += 'partition by'
                if len(over['frame_boundaries']['preceding']) > 0 :
                    c += f" between {over['frame_boundaries']['preceding']}  and {over['frame_boundaries']['following']}"

                c += f") as {col['name']}"

                columns.append(c)

        sql += f"{','.join(columns)}"
        # print(cte)
        sql += f" from {','.join(cte['from'])}"


        order_by = cte['order'][0]
        order_type = cte['order'][1]
        sql += f" order by {order_by} {order_type} " if len(
            order_by) > 0 else ''
    

        if 'limit' in cte.keys():          
            limit = cte['limit']
            if limit['number'] > 0:
                sql += f"limit {limit['number']}"
                if limit['offset'] > 0:
                    sql += f" limit['offset']"

        # END OF CTE
        sql += f") select * from {cte['name']} limit 100"
    print(sql)
    return sql
