# =========================
# Author: Kai Leon Deines
# =========================


def list_table(table: list):
    # construct html table from list
    html = '<style>body,table{font-family:"Tahoma";font-size:12px;}table,tr,th,' \
           'td{border:1px solid black;border-collapse:collapse;vertical-align:top;}th{background:#ccc}</style><table> '

    # fill in the cells
    for row in table:
        html = html + '<tr>'
        row.pop(len(row) - 1)  # remove the last cell from each row as it's always empty

        if row == table[0]:
            for col in row:
                html = html + '<th>' + str(col).replace('', '').replace('', '').replace('', '') + '</th>'
        else:
            if row == table[0]:
                print('hi')

            else:
                for col in row:
                    html = html + '<td>'
                    for e in col:
                        # an element list contains only one or two items (content and/or link)
                        if len(e) == 2:
                            # TODO: replace links
                            html = html + '<a href="' + str(e[1]) + '">' + str(e[0]) + '</a>\n'
                        else:
                            html = html + '<p>' + str(e[0]) + '</p>\n'

                    html = html + '</td>'

                html = html + '</tr>'

    html = html + '</table>'

    return html
