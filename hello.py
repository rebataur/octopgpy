from flask import Flask,render_template,request,jsonify
import json


import psycopg2
from psycopg2.extras import RealDictCursor


conn = psycopg2.connect(
        host="localhost",
        database="postgres",
        user="postgres",
        password="postgres"
)


cur = conn.cursor(cursor_factory=RealDictCursor)
# Open a cursor to perform database operations

# import sqlite3

app = Flask(__name__)

@app.route('/')
def hello(name=None):
    return render_template('hello.html', name="dfdfdf")

@app.route('/jsontosql',methods=['POST'])
def jsontosql():
    print(request.get_json())    
    jsonsql = request.get_json()
    with open('test.json','w') as f:
        f.write(json.dumps(jsonsql,  indent=4,default=str))
    sql = jsontosql(jsonsql)
    cur.execute(sql)
    res = cur.fetchall()
    # res = []
    jsonres = json.dumps(res,  indent=4, sort_keys=True, default=str)
    return json.dumps({'success':True,'sql':sql,'res':jsonres}), 200, {'ContentType':'application/json'} 

def jsontosql(jsonsql):  
    operators_dict= {'+':'+','-':'-','=':'=','lt':'<','gt':'>','lte':'<=', 'gte':'>='}
    ctes = [jsonsql]
    sql = ''
    i = 0
    for cte in ctes:

        if i == 0:
            sql += f"WITH {cte['name']} AS( SELECT  "
        else:
            sql += f", {cte['name']} as ( SELECT  "

        columns = []
       
        for col in cte['cols']:
            print(col)
            print(col['type'])
            col_type = col['type']
            col_name = col['name']
            

            # Normal Column
            if col_type == "normal":
                columns.append(col_name)

            # Window function
            elif col_type == 'window_function':
                attribs = col['attributes']
                c = ""
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

                c += " OVER("
                over = attribs['over']
                # print(over)

               
                frame_spec = over['frame_spec']
                if over['partition_by'] != '':
                    c += f"PARTITION BY{over['partition_by']}"

                order_by = over['order_by']
                order_type = over['order_type']

                c += f" ORDER BY {order_by} {order_type} " if len(
                    order_by) > 0 else ''


                if frame_spec['type'] == 'rows':
                    c += 'ROWS '

                elif frame_spec['type'] == 'range':
                   c += 'RANGE '
                elif frame_spec['type'] == 'group':
                   c += 'GROUP '
             
                if len(over['frame_boundaries']['preceding']) > 0 :
                    c += f" BETWEEN {over['frame_boundaries']['preceding']}  AND {over['frame_boundaries']['following']}"

                c += f") as {col_name}"

                columns.append(c)

            # Case columns
            elif col_type == 'case':
                attribs = col['attributes']
                c = "CASE WHEN "
                for a in attribs['when']:
                    if a in operators_dict.keys():
                        c += " " + operators_dict[a] 
                    else:
                        c += " " + a
                c += ' THEN ' + attribs['then'] + " END " + col_name
                columns.append(c)

        sql += f"{','.join(columns)}"
        # print(cte)
        sql += f" FROM {','.join(cte['from'])}"


        # Where clause
        if len(cte['where']) > 0:
            sql += " WHERE "  
            for w in cte['where']:
                if w in operators_dict.keys():
                    sql += " " + operators_dict[w] 
                else:
                    sql += " " + w


        # Order by
        if len(cte['order']) > 0:
            sql += " ORDER BY "
            for o in cte['order']:            
                sql += o + " "
                if o in ['asc','desc']:
                    sql += ","
            sql = sql[:-1]
        # order_by = cte['order'][0]
        # order_type = cte['order'][1]
        # sql += f" order by {order_by} {order_type} " if len(
        #     order_by) > 0 else ''
    

        if 'limit' in cte.keys():          
            limit = cte['limit']
            if limit['number'] > 0:
                sql += f"limit {limit['number']}"
                if limit['offset'] > 0:
                    sql += f" limit['offset']"

        # END OF CTE
        sql += f") select * from {cte['name']} limit 10"
    print(sql)
    return sql
