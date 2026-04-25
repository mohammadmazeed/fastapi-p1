from fastapi import FastAPI
from fastapi.responses import HTMLResponse
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

@app.get("/", response_class=HTMLResponse)
def read_root():
    conn = psycopg2.connect(conn_string)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM employee")
    count = cur.fetchone()[0]
    cur.close()
    conn.close()
    html = """
    <html>
      <head>
        <title>Employee Dashboard</title>
        <style>
          body { font-family: Arial, sans-serif; margin: 0; padding: 0; background: #f5f7fb; color: #2c3e50; }
          .container { max-width: 1024px; margin: 0 auto; padding: 24px; }
          h1 { text-align: center; margin-bottom: 16px; }
          .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 18px; margin-top: 24px; }
          .box { background: #fff; border-radius: 16px; padding: 24px; box-shadow: 0 12px 28px rgba(15, 23, 42, 0.08); text-align: center; }
          .box h2 { margin: 0 0 12px; font-size: 1.15rem; }
          .box p { font-size: 2.4rem; margin: 0; color: #1e40af; }
          .box button { margin-top: 16px; padding: 10px 18px; border: none; border-radius: 10px; background: #1e40af; color: #fff; cursor: pointer; transition: background 0.2s ease; }
          .box button:hover { background: #1d4ed8; }
          .modal-backdrop { display: none; position: fixed; inset: 0; background: rgba(15, 23, 42, 0.45); z-index: 20; justify-content: center; align-items: flex-end; }
          .modal { width: 100%; max-width: 700px; background: #fff; border-radius: 24px 24px 0 0; padding: 24px; box-shadow: 0 -20px 60px rgba(15, 23, 42, 0.2); }
          .modal h3 { margin-top: 0; }
          .modal .form-row { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; }
          .modal label { display: block; margin-bottom: 6px; font-weight: 600; }
          .modal input { width: 100%; padding: 10px 12px; border: 1px solid #cbd5e1; border-radius: 10px; }
          .modal textarea { width: 100%; min-height: 120px; padding: 10px 12px; border: 1px solid #cbd5e1; border-radius: 10px; }
          .modal-actions { display: flex; justify-content: flex-end; gap: 12px; margin-top: 20px; }
          .modal-actions button { min-width: 120px; }
          .secondary { background: #e2e8f0; color: #0f172a; }
          .secondary:hover { background: #cbd5e1; }
          .success { background: #10b981; }
          .success:hover { background: #059669; }
          .quote { text-align: center; margin-top: 32px; color: #475569; }
        </style>
      </head>
      <body>
        <div class="container">
          <h1>Employee Dashboard</h1>
          <div class="grid">
            <div class="box">
              <h2>Total Employees</h2>
              <p>##COUNT##</p>
            </div>
            <div class="box">
              <h2>Edit Records</h2>
              <button onclick="openModal('edit')">Open Edit Form</button>
            </div>
            <div class="box">
              <h2>Create New Employee</h2>
              <button onclick="openModal('create')">Open Create Form</button>
            </div>
            <div class="box">
              <h2>Database</h2>
              <p>PostgreSQL</p>
            </div>
          </div>
          <p class="quote">Use the forms below to create or edit employees directly from this page.</p>
        </div>

        <div id="modal" class="modal-backdrop" onclick="closeModal(event)">
          <div class="modal" onclick="event.stopPropagation()">
            <h3 id="modal-title">Create Employee</h3>
            <div class="form-row">
              <div>
                <label for="emp_id">Employee ID</label>
                <input type="number" id="emp_id" />
              </div>
              <div>
                <label for="first_name">First Name</label>
                <input type="text" id="first_name" />
              </div>
              <div>
                <label for="last_name">Last Name</label>
                <input type="text" id="last_name" />
              </div>
              <div>
                <label for="age">Age</label>
                <input type="number" id="age" />
              </div>
              <div>
                <label for="department">Department</label>
                <input type="text" id="department" />
              </div>
              <div>
                <label for="salary">Salary</label>
                <input type="number" id="salary" step="0.01" />
              </div>
              <div>
                <label for="hire_date">Hire Date</label>
                <input type="date" id="hire_date" />
              </div>
            </div>
            <div class="modal-actions">
              <button class="secondary" onclick="closeModal()" type="button">Cancel</button>
              <button class="success" id="modal-submit" type="button">Save</button>
            </div>
          </div>
        </div>

        <script>
          let currentMode = 'create';

          function openModal(mode) {
            currentMode = mode;
            document.getElementById('modal-title').textContent = mode === 'edit' ? 'Edit Employee' : 'Create Employee';
            document.getElementById('emp_id').disabled = mode === 'edit';
            if (mode === 'edit') {
              const empId = prompt('Enter emp_id to edit:');
              if (!empId) return;
              fetch(`/employees/${empId}`)
                .then(response => response.json())
                .then(data => {
                  if (data.error) {
                    alert(data.error);
                    return;
                  }
                  document.getElementById('emp_id').value = data.emp_id;
                  document.getElementById('first_name').value = data.first_name;
                  document.getElementById('last_name').value = data.last_name;
                  document.getElementById('age').value = data.age;
                  document.getElementById('department').value = data.department;
                  document.getElementById('salary').value = data.salary;
                  document.getElementById('hire_date').value = data.hire_date;
                  document.getElementById('modal').style.display = 'flex';
                })
                .catch(() => alert('Unable to load employee data.'));
            } else {
              clearForm();
              document.getElementById('modal').style.display = 'flex';
            }
          }

          function closeModal(event) {
            if (event && event.target !== event.currentTarget) return;
            document.getElementById('modal').style.display = 'none';
          }

          function clearForm() {
            document.getElementById('emp_id').value = '';
            document.getElementById('first_name').value = '';
            document.getElementById('last_name').value = '';
            document.getElementById('age').value = '';
            document.getElementById('department').value = '';
            document.getElementById('salary').value = '';
            document.getElementById('hire_date').value = '';
          }

          document.getElementById('modal-submit').addEventListener('click', () => {
            const employee = {
              emp_id: Number(document.getElementById('emp_id').value),
              first_name: document.getElementById('first_name').value,
              last_name: document.getElementById('last_name').value,
              age: Number(document.getElementById('age').value),
              department: document.getElementById('department').value,
              salary: Number(document.getElementById('salary').value),
              hire_date: document.getElementById('hire_date').value
            };

            const url = currentMode === 'edit' ? `/employees/${employee.emp_id}` : '/employees/';
            const method = currentMode === 'edit' ? 'PUT' : 'POST';

            fetch(url, {
              method,
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify(employee)
            })
              .then(response => response.json())
              .then(data => {
                alert(data.message || JSON.stringify(data));
                if (!data.error) {
                  closeModal();
                  location.reload();
                }
              })
              .catch(() => alert('Unable to save employee.'));
          });
        </script>
      </body>
    </html>
    """
    html = html.replace("##COUNT##", str(count))
    return HTMLResponse(content=html)

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
    if row:
        columns = [desc[0] for desc in cur.description]
        result = dict(zip(columns, row))
    else:
        result = {"error": "Employee not found"}
    cur.close()
    conn.close()
    return result

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


