from flask import Flask,render_template,request,jsonify,Response
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


@app.route('/viz',methods=['GET'])
def visualization():
    sql = '''
            WITH test AS(
            SELECT
                trade_date,
                code,
                CLOSE,
                name,
                AVG(round(CLOSE)) OVER(PARTITION BY code
            ORDER BY
                trade_date ROWS BETWEEN 199 PRECEDING AND CURRENT ROW) AS sma200
            FROM
                BSE
            ORDER BY
                trade_date DESC 
            
                
        ), lmt as(
                
        select close,sma200,trade_date,name
        FROM
            test
        WHERE
            code = 532540
            limit 200
        )select array_agg(name) as namearr,array_agg(close) as closearr,array_agg(sma200) as smaarr,array_agg(trade_date) as trade_datearr from lmt 

    '''

    cur.execute(sql)
    res = cur.fetchall()

    name = res[0]['namearr'][0]
    closearr = res[0]['closearr']
    smaarr = res[0]['smaarr']
    tradearr = res[0]['trade_datearr']

    
    from io import BytesIO
    import matplotlib as mpl
    mpl.use('Agg')
    import matplotlib.pyplot as plt
    # import numpy as np

    plt.rcParams["figure.figsize"] = [7.50, 3.50]
    plt.rcParams["figure.autolayout"] = True

    # x = np.linspace(0, 2, 100)  # Sample data.
    plt.figure(figsize=(10, 5), layout='constrained')
    plt.plot(tradearr, closearr, label='close')  # Plot some data on the (implicit) axes.
    plt.plot(tradearr,smaarr, label='sma200')  # etc.
    plt.xlabel('close, sma200')
    plt.ylabel('trade date')
    plt.title(name)
    plt.legend()

    buffer = BytesIO()
    plt.savefig(buffer, format="png")
    return Response(buffer.getvalue(), mimetype='image/png')




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
                    c += f"PARTITION BY {over['partition_by']}"

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
                c += ' THEN ' + attribs['then'] + " ELSE " + attribs['else'] + "END as " + col_name
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
    


        # END OF CTE
        sql += f") select * from {cte['name']} limit {cte['limit']} offset {cte['offset']}"
    print(sql)
    return sql
