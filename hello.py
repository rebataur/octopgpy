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


# cur = conn.cursor(cursor_factory=RealDictCursor)
# Open a cursor to perform database operations

# import sqlite3

app = Flask(__name__)
@app.route('/v')
def v(name=None):
    # tablemeta = fetch_all_tables_meta()
    return render_template('v.html')

@app.route('/')
def hello(name=None):
    tablemeta = fetch_all_tables_meta()
    return render_template('hello.html', table_meta=tablemeta)

@app.route('/jsontosql/<action>',methods=['POST'])
def jsontosql(action):
    print(action)
    print(request.form)
    print("================================")

    print("Request",request.get_json())
    jsonsql = request.get_json()

    with open('test.json','w') as f:
        f.write(json.dumps(jsonsql,  indent=4,default=str))

    sql = get_jsontosql(jsonsql)
    full_sql = saveCTE(jsonsql,sql,action)
    print("SQL ",full_sql)
    res = fetch_sql(full_sql)
    
    jsonres = json.dumps(res,  indent=4, sort_keys=True, default=str)
    return json.dumps({'success':True,'sql':sql,'res':jsonres}), 200, {'ContentType':'application/json'} 

    return json.dumps({'success':False,'sql':'','res':''}), 200, {'ContentType':'application/json'} 
    
@app.route('/fetchtablemeta',methods=['POST'])
def fetchtablemeta():
    fromlist = request.get_json()
    tablemeta = fetch_all_tables_meta()
    print(fromlist,tablemeta)
    db_cols = ['',];
    for t in tablemeta:
        print(t['name'],fromlist,t['name'] in fromlist)
        if t['name'] in fromlist:
            for c in t['cols']:
                db_cols.append(f"{t['name']}.{c['name']}")
    print(db_cols)
    return json.dumps({'success':True,'res':db_cols}), 200, {'ContentType':'application/json'} 

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

    

    res = execute_sql(sql)

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

def get_jsontosql(jsonsql):  
    operators_dict= {'+':'+','-':'-','=':'=','lt':'<','gt':'>','lte':'<=', 'gte':'>='}
    ctes = jsonsql
    print(jsonsql)
    print("------------------------------")
    sql = ''
    print(ctes)
    for cte in ctes:        
        print("=================================")
        print(len(cte))
        if cte['parent'] == "":
            sql += f"WITH {cte['name']} AS ( SELECT  "
        else:
            sql += f" ) , {cte['name']} as ( SELECT  "
        columns = []

        for col in cte['cols']:
            print(col)
            print(col['type'])
            col_type = col['type']
            col_name = col['name']

            # Normal Column
            if col_type == "normal":
                columns.append(f'{col_name} as {col_name.replace(".","_")}')
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
        sql += f" FROM {' '.join(cte['from'])}"
        # Where clause
        print((cte['where']))

        if len(cte['where']) > 0:
            sql += " WHERE "  
            operand_found = False
            for w in cte['where']:               
                if w in operators_dict.keys():
                    sql += " " + operators_dict[w] 
                    operand_found = True
                else:
                    if operand_found and not w.isnumeric():
                                              
                        sql += f"'{w}'"
                        print(sql)
                        operand_found = False
                    else:
                        sql += f"{w}"
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

def saveCTE(jsontosql,generated_sql,action):

    jsontosql = jsontosql[0]
    # generated_sql = generated_sql.replace("'","''")
    sql = '''
        create table if not exists CTE(name text unique,ctejson json, ctesql text,parent text)
    '''
    execute_sql(sql)
    # sql = f'''
    #     insert into 
    #     CTE(name,ctejson,ctesql,parent) 
    #     values('{jsontosql["name"]}','{json.dumps(jsontosql)}','{generated_sql}','{jsontosql['parent']}')

    #     on conflict(name)
    #     DO 
    #     update set ctejson = '{json.dumps(jsontosql)}', ctesql = '{generated_sql}', parent =  '{jsontosql['parent']}'
    # '''
    if jsontosql['parent'] == '':
        sql = f'''
            insert into 
            CTE(name,ctejson,ctesql,parent) 
            values('{jsontosql["name"]}','{json.dumps([jsontosql])}','{generated_sql.replace("'","''")}','{jsontosql['parent']}')
        '''
       
        if action == 'save':           
            execute_sql(sql)
        return generated_sql
    else:
        sql = f'''
            SELECT * FROM CTE WHERE name = '{jsontosql['parent']}'
        '''
        res = fetch_sql(sql)
        jsql = res[0]['ctejson']
        jsql_dict = jsql
        # cte_arr = []
        # cte_arr.append(jsql_dict)
        jsql_dict.append(jsontosql)
        full_sql = get_jsontosql(jsql_dict)
     
        sql = f'''
            update cte set name = '{jsontosql["name"]}', ctejson = '{json.dumps(jsql_dict)}', ctesql = '{full_sql.replace("'","''")}' where name = '{jsontosql["parent"]}'
        '''
        if action == 'save':
            execute_sql(sql)
        return full_sql
    
    
def execute_sql(sql):
    print(" Executing SQL ", sql)    
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        try:
            cur.execute(sql)
            conn.commit()
        except psycopg2.errors.InFailedSqlTransaction as e:
            print("THERE WAS ERROR IN EXECUTING SQL")
            print(sql)
            print(e)
            cur.execute("ROLLBACK")
            conn.commit()
      
    
   
def fetch_sql(sql):
    print(" Fetching SQL ", sql)
    res = []
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        try:
            cur.execute(sql)
            res = cur.fetchall()
            return res
        except psycopg2.errors.InFailedSqlTransaction as e:
            print("THERE WAS ERROR IN EXECUTING SQL")
            print(sql)
            print(e)
            cur.execute("ROLLBACK")
            conn.commit()
            return res


def fetch_all_tables_meta():
    sql = '''
        SELECT * FROM information_schema.tables WHERE table_schema = 'public'
    '''
    res = fetch_sql(sql)
    table_struct = []
    for t in res:
        tname = t['table_name']
        tstruct = {}
        if tname == 'cte':    
            # get cte sql
            sql = '''
                  select * from cte
            '''
            ctes = fetch_sql(sql)
            for cte in ctes:
                sql = '''
                    drop table if exists cte_temp
                '''
                execute_sql(sql)
                clean_sql = cte['ctesql'].replace("''","'")
                sql = f"create table cte_temp as {clean_sql}"
                execute_sql(sql)
                cols = get_table_columns('cte_temp')
                table_struct.append({
                    "name":cte['name'],
                    "type" : "cte",
                    "cols":cols
                })
                sql = '''
                    drop table if exists cte_temp
                '''
                execute_sql(sql)
              

        elif tname != 'cte_temp':
            cols = get_table_columns(tname)
            table_struct.append({
                "name":tname,
                "type" : 'table',
                "cols":cols
            })
    return table_struct

def get_table_columns(tname): 
    sql = f'''
        SELECT column_name, data_type 
        FROM information_schema.columns
        WHERE table_name = '{tname}' AND table_schema = 'public';
    '''
    table_cols = fetch_sql(sql)
   
    cols = []
    for col in table_cols:
        cols.append({"name":col['column_name'],'type':col['data_type']})
    # print("GET TABLE COLUMN",tname,sql,table_cols,cols)

    return cols

