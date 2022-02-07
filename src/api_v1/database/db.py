import psycopg2

class DatabaseAnalytic(object):
    def __init__(self, database, user, password, host, port):
        self.conn = psycopg2.connect(database=database, 
                                     user=user, 
                                     password=password,
                                     host=host,
                                     port=port)
        # setting autocommit false
        self.conn.autocommit = False
        
    def get_threshold_actual(self, sensors):
        conn = self.conn
        cursor = conn.cursor()
        query = """
        SELECT id, actual_low, actual_high FROM sensors
        WHERE name IN {};""".format(tuple(sensors))
        cursor.execute(query)
        result = cursor.fetchall()
        conn.commit()

        # separate result
        id = [r[0] for r in result]
        actual_low = [r[1] for r in result]
        actual_high = [r[2] for r in result]

        cursor.close()
        return id, actual_low, actual_high

    def get_residual_threshold(self, id_sensor):
        conn = self.conn
        cursor = conn.cursor()
        query = """
        SELECT residual_positive_threshold, residual_negative_threshold FROM model_tag
        WHERE sensor IN {};""".format(tuple(id_sensor))
        cursor.execute(query)
        result = cursor.fetchall()
        conn.commit()

        # separate result
        residual_positive_threshold = [r[0] for r in result]
        residual_negative_threshold = [r[1] for r in result]

        cursor.close()
        return residual_positive_threshold, residual_negative_threshold

    def insert_to_runtime(self, values):
        conn = self.conn
        cursor = conn.cursor()
        for row in values:
            cursor.execute("""
                INSERT INTO runtime (timestamp, sensor, actual, actual_smoothed, estimate, residual, residual_smoothed, residual_indication_positive, residual_indication_negative)
                VALUES (%s, %s, %s, NULL, %s, %s, NULL, %s, %s);""", (
                row[0],
                row[1],
                row[2],
                row[4],
                row[5],
                row[7],
                row[8],
            ))
        conn.commit()
        cursor.close()