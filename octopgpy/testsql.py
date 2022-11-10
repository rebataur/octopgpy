
cte = {
    "name": "sma",
    "from": ["bse"],
    "order_by": "trade_date",
                "order_type": "desc",
                "limit": {"number": 0, "offset": 0},
                "cols": [
                    {
                        "name": "trade_date",
                        "type": "normal"
                    },
                    {
                        "name": "close",
                        "type": "normal"
                    },
                    {
                        "fname": "is_sma200_rising",
                        "type": "case",
                        "attributes": [
                            {"when": {
                                "field": "sma_diff",
                                        "operator": ">",
                                        "value": 0
                            },
                                "then": "TRUE",
                                "else": "FALSE"
                            }

                        ]
                    },
                    {
                        "name": "sma20",
                        "type": "window_function",
                        "attributes":
                            {
                                "window_func": "avg",
                                "col": "close",                             
                                "over": {
                                    "partition_by": "",
                                    "order_by": "trade_date",
                                    "order_type": "desc",
                                    "frame_spec": {
                                        "meta": {
                                            "types": [
                                                "rows",
                                                "groups",
                                                "range"
                                            ]
                                        },
                                        "type": "rows"
                                    },
                                    "frame_boundaries": {
                                        "meta": {
                                            "types": [
                                                "unbounded_preceding",
                                                "preceding",
                                                "current_row",
                                                "following",
                                                "unbounded_following"
                                            ]
                                        },
                                     
                                        "preceding": 19,
                                        "following": "current row"
                                    }
                                }
                            },
                    }
    ],
    "where": {
                    "criterion": {
                        "and": {"field":"code", "operator":"=","value":343453}
                    }
    }
}


cte = {
    "name": "sma",
    "from": [
        "BSE"
    ],
    "cols": [
        {
            "name": "trade_date",
            "type": "normal"
        },
        {
            "name": "code",
            "type": "normal"
        },
        {
            "name": "close",
            "type": "normal"
        },
        {
            "name": "name",
            "type": "normal"
        },
        {
            "name": "sma200",
            "type": "window_function",
            "attributes": {
                "window_func": "AVG",
                "col": "close",
                "over": {
                    "partition_by": "",
                    "order_by": "trade_date",
                    "order_type": "desc",
                    "frame_spec": {
                        "type": "rows"
                    },
                    "frame_boundaries": {
                        "preceding": "199 preceding",
                        "following": "current Row"
                    }
                }
            }
        },
        {
            "name": "close_lt_1000",
            "type": "case",
            "attributes": {
                "when": [
                    "close",
                    "lt",
                    "1000",
                    ""
                ],
                "then": "value"
            }
        }
    ],
    "where": [
        "code",
        "lt",
        "56000",
        ""
    ],
    "order": [
        "trade_date",
        "desc"
    ]
}
ctes = [cte]
if __name__ == '__main__':
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
        sql += f") select * from {cte['name']}"
    print(sql)
