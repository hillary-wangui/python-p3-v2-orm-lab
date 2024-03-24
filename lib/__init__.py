import sqlite3

from lib.employee import Employee

CONN = sqlite3.connect("company.db")
CURSOR = CONN.cursor()


class Review:
    def __init__(self, year, summary, employee_id, id=None):
        self.year = year
        self.summary = summary
        self.employee_id = employee_id
        self.id = id
        self.all = {}

    @property
    def year(self):
        return self._year

    @year.setter
    def year(self, value):
        if value < 2000:
            raise Exception("Year should be an integer that is greater than or equal to 2000.")
        self._year = value

    @property
    def summary(self):
        return self._summary

    @summary.setter
    def summary(self, value):
        if not value:
            raise Exception("Summary should be a non-empty string.")
        self._summary = value

    @property
    def employee_id(self):
        return self._employee_id

    @employee_id.setter
    def employee_id(self, value):
        if not isinstance(value, int) or Employee.get_by_id(value) is None:
            raise Exception("Employee_id should be the id of an Employee class instance that has been persisted into the 'employees' table.")
        self._employee_id = value

    @classmethod
    def create_table(cls):
        table_schema = """
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            year INTEGER NOT NULL,
            summary TEXT NOT NULL,
            employee_id INTEGER NOT NULL,
            FOREIGN KEY(employee_id) REFERENCES employees(id)
        );
        """
        CURSOR.execute(table_schema)
        CONN.commit()

    @classmethod
    def drop_table(cls):
        CURSOR.execute("DROP TABLE IF EXISTS reviews;")
        CONN.commit()

    def save(self):
        query = "INSERT INTO reviews (year, summary, employee_id) VALUES (?, ?, ?);"
        CURSOR.execute(query, (self.year, self.summary, self.employee_id))
        self.id = CURSOR.lastrowid
        self.all[self.id] = self
        CONN.commit()

    @classmethod
    def create(cls, year, summary, employee_id):
        new_review = cls(year, summary, employee_id)
        new_review.save()
        return new_review

    @classmethod
    def instance_from_db(cls, id):
        query = "SELECT * FROM reviews WHERE id = ?;"
        result = CURSOR.execute(query, (id,))
        if result.fetchone() is None:
            return None
        review_data = result.fetchone()
        return cls(review_data[1], review_data[2], review_data[3], id=review_data[0])

    @classmethod
    def find_by_id(cls, id):
        review_instance = cls.instance_from_db(id)
        if review_instance is None:
            return None
        return review_instance

    def update(self):
        query = "UPDATE reviews SET year = ?, summary = ?, employee_id = ? WHERE id = ?;"
        CURSOR.execute(query, (self.year, self.summary, self.employee_id, self.id))
        CONN.commit()

    def delete(self):
        query = "DELETE FROM reviews WHERE id = ?;"
        CURSOR.execute(query, (self.id,))
        self.id = None
        CONN.commit()

    @classmethod
    def get_all(cls):
        query = "SELECT *FROM reviews;"
        result = CURSOR.execute(query)
        review_instances = []
        for row in result.fetchall():
            review_instances.append(
                cls(row[1], row[2], row[3], id=row[0]))
        return review_instances

    def __repr__(self):
        return (
            f"<Review id: {self.id}, year: {self.year}, "
            f"summary: {self.summary}, employee_id: {self.employee_id}>"
        )