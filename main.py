from fastapi import FastAPI
from pydantic import BaseModel
import psycopg2
from datetime import date

app = FastAPI()

class Item(BaseModel):
    name: str
    price: float

class Employee(BaseModel):
    emp_id: int
    first_name: str
    last_name: str
    age: int
    department: str
    salary: float
    hire_date: date

class SQLQuery(BaseModel):
    query: str

conn_string = "postgresql://neondb_owner:npg_EFh92rmIvfSZ@ep-weathered-water-amc2inge-pooler.c-5.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/items/")
def create_item(item: Item):
    return item

@app.get("/employees/")
def get_employees():
    conn = psycopg2.connect(conn_string)
    cur = conn.cursor()
    cur.execute("SELECT * FROM employee")
    rows = cur.fetchall()
    columns = [desc[0] for desc in cur.description]
    employees = [dict(zip(columns, row)) for row in rows]
    cur.close()
    conn.close()
    return employees

@app.get("/employees/{emp_id}")
def get_employee(emp_id: int):
    conn = psycopg2.connect(conn_string)
    cur = conn.cursor()
    cur.execute("SELECT * FROM employee WHERE emp_id = %s", (emp_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    if row:
        columns = [desc[0] for desc in cur.description]
        return dict(zip(columns, row))
    else:
        return {"error": "Employee not found"}

@app.put("/employees/{emp_id}")
def update_employee(emp_id: int, employee: Employee):
    conn = psycopg2.connect(conn_string)
    cur = conn.cursor()
    cur.execute("UPDATE employee SET first_name=%s, last_name=%s, age=%s, department=%s, salary=%s, hire_date=%s WHERE emp_id=%s",
                (employee.first_name, employee.last_name, employee.age, employee.department, employee.salary, employee.hire_date, emp_id))
    conn.commit()
    cur.close()
    conn.close()
    return {"message": "Employee updated"}

@app.post("/employees/")
def create_employee(employee: Employee):
    conn = psycopg2.connect(conn_string)
    cur = conn.cursor()
    cur.execute("INSERT INTO employee (emp_id, first_name, last_name, age, department, salary, hire_date) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (employee.emp_id, employee.first_name, employee.last_name, employee.age, employee.department, employee.salary, employee.hire_date))
    conn.commit()
    cur.close()
    conn.close()
    return {"message": "Employee created"}

@app.post("/execute/")
def execute_query(sql: SQLQuery):
    conn = psycopg2.connect(conn_string)
    cur = conn.cursor()
    cur.execute(sql.query)
    if sql.query.strip().upper().startswith("SELECT"):
        rows = cur.fetchall()
        columns = [desc[0] for desc in cur.description]
        result = [dict(zip(columns, row)) for row in rows]
    else:
        conn.commit()
        result = {"message": "Query executed"}
    cur.close()
    conn.close()
    return result


