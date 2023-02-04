import mysql.connector


class credentials:    
    data_base = mysql.connector.connect(host='127.0.0.1',
                                        user='root',
                                        passwd='mysql@1419',
                                        db='bookmyshow',
                                        port=3306)


