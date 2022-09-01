# =========================
# Author: Kai Leon Deines
# =========================


def list_table(table: list) :
    # construct html table from list
    html = '<html><meta charset="utf-8"><body><style> body,table,tr,td {font-family:"Arial";font-size:12px;} ' \
           'table, tr, td {border:1px solid black;border-collapse:collapse;vertical-align:top;} </style><table>'

    # construct table header row
    html = html + '<tr>'



    for column_header_column in columns_header_columns:
        html = html + '<th>' + column_header_column.text.replace('', '', 1).replace('', '', 1).replace('', '',
                                                                                                        1) + '</th>'

    html = html + '</tr>'

    # fill in the cells
    for row in table:
        html = html + '<tr>'
        row.pop(len(row) - 1)  # remove the last cell from each row as it's always empty

        for col in row:
            html = html + '<td>'

            for e in col:
                # an element list contains only one or two items (content and/or link)
                if len(e) == 2:
                    html = html + '<a href="' + str(e[1]) + '">' + str(e[0]) + '</a>\n'
                else:
                    html = html + '<p>' + str(e[0]) + '</p>\n'

            html = html + '</td>'

        html = html + '</tr>'

    html = html + '</table></body></html>'

    return html