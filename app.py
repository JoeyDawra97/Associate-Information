from fastapi import FastAPI, HTTPException, Form
from fastapi.responses import HTMLResponse, RedirectResponse
import asyncpg
import uvicorn
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Instantiate FastAPI app
app = FastAPI()

# Define database URL for async connection using asyncpg
DATABASE_URL = 'postgresql://postgres:******@127.0.0.1:5432/website'

# Create a connection pool
async def create_pool():
    return await asyncpg.create_pool(DATABASE_URL)

pool = None

# Define the startup event to create the connection pool
@app.on_event("startup")
async def startup_event():
    global pool
    pool = await create_pool()
    async with pool.acquire() as conn:
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS associates_info (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                hire_date DATE NOT NULL,
                manager TEXT NOT NULL,
                department TEXT NOT NULL
            )
        ''')

# Define a simple root route
@app.get("/")
async def read_root():
    html_content = """
    <html>
    <head>
        <title>Home Page</title>
        <style>
            body { background-color: #DBDBDB; font-family: Arial, sans-serif; text-align: center; margin-top: 50px; }
            h1 { color: Blue; text-align: center; font-style: italic; font-family: "Roboto", serif; font-weight: bold; text-decoration: underline; }
            .link-container { margin-top: 20px; }
            .link-container a { display: inline-block; margin: 10px; padding: 10px 20px; background-color: #4CAF50; color: white; text-decoration: none; border-radius: 5px; }
            .link-container a:hover { background-color: #45a049; }
            .form-container { margin-top: 20px; }
            .form-container input[type=number], .form-container input[type=text] { padding: 10px; margin: 5px; }
            .form-container input[type=submit] { padding: 10px 20px; margin: 5px; background-color: #4CAF50; color: white; border: none; cursor: pointer; }
            .form-container input[type=submit]:hover { background-color: #45a049; }
        </style>
    </head>
    <body>
        <h1>Welcome to the Associates Information System</h1>
        <div class="link-container">
            <a href="/associates">View Associates</a>
        </div>
        <div class="form-container">
            <form action="/lookup_associate" method="post">
                <input type="number" name="id" placeholder="Enter Associate ID">
                <input type="text" name="name" placeholder="Enter Name">
                <input type="text" name="manager" placeholder="Enter Manager">
                <input type="text" name="department" placeholder="Enter Department">
                <input type="submit" value="Look Up">
            </form>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

# Define the lookup route to fetch and display associate information
@app.post("/lookup_associate", response_class=HTMLResponse)
async def lookup_associate(
        id: int = Form(None),
        name: str = Form(None),
        manager: str = Form(None),
        department: str = Form(None)
):
    query = "SELECT * FROM associates_info WHERE "
    conditions = []
    values = []

    if id:
        conditions.append("id = $" + str(len(conditions) + 1))
        values.append(id)
    if name:
        conditions.append("name ILIKE $" + str(len(conditions) + 1))
        values.append(f"%{name}%")
    if manager:
        conditions.append("manager ILIKE $" + str(len(conditions) + 1))
        values.append(f"%{manager}%")
    if department:
        conditions.append("department ILIKE $" + str(len(conditions) + 1))
        values.append(f"%{department}%")

    if not conditions:
        raise HTTPException(status_code=400, detail="At least one search criteria must be provided")

    query += " AND ".join(conditions)

    logger.info(f"Executing query: {query} with values {values}")

    try:
        async with pool.acquire() as conn:
            associates = await conn.fetch(query, *values)
            if not associates:
                html_content = """
                 <html>
                <head>
                    <style>
                        body {
                            background-color: #DBDBDB;
                            font-family: Arial, sans-serif;
                            text-align: center;
                            margin-top: 50px;
                        }
                        h2 { 
                            color: Blue; 
                            text-align: center; 
                            font-style: italic; 
                            font-family: "Roboto", serif; 
                            font-weight: bold; 
                            text-decoration: underline; }
                        
                        .back-button {
                            display: inline-block;
                            margin: 10px;
                            padding: 10px 20px;
                            background-color: #4CAF50;
                            color: white;
                            text-decoration: none;
                            border-radius: 5px;
                            font-weight: bold;
                            font-size: 16px;
                            transition: background-color 0.3s;
                        }
                        .back-button:hover {
                            background-color: #45a049;
                        }
                    </style>
                </head>
                <body>
                    <h2>No associate found with the provided criteria</h2>
                    <a href="/" class="back-button">Back to Home</a>
                </body>
                </html>
                """
                return HTMLResponse(content=html_content)

            html_content = """
            <html>
            <head>
                <title>Associate Information</title>
                <style>
                    body {
                        background-color: #DBDBDB;
                        font-family: Arial, sans-serif;
                        text-align: center;
                        margin-top: 50px;
                    }

                    .info-container {
                        display: inline-block;
                        text-align: left;
                        margin-top: 20px;
                        padding: 20px;
                        background-color: #ffffff;
                        border: 1px solid #ddd;
                        border-radius: 10px;
                    }

                    .info-container h2 {
                        color: #0404F5;
                    }

                    .back-button {
                        display: inline-block;
                        margin: 10px;
                        padding: 10px 20px;
                        background-color: #4CAF50;
                        color: white;
                        text-decoration: none;
                        border-radius: 5px;
                    }

                    .back-button:hover {
                        background-color: #45a049;
                    }
                </style>
            </head>
            <body>
            """

            for associate in associates:
                html_content += f"""
                <div class="info-container">
                    <h2>Associate Information</h2>
                    <p><strong>ID:</strong> {associate['id']}</p>
                    <p><strong>Name:</strong> {associate['name']}</p>
                    <p><strong>Hire Date:</strong> {associate['hire_date']}</p>
                    <p><strong>Manager:</strong> {associate['manager']}</p>
                    <p><strong>Department:</strong> {associate['department']}</p>
                </div>
                """

            html_content += """
                <a href="/" class="back-button">Back to Home</a>
            </body>
            </html>
            """
            return HTMLResponse(content=html_content)
    except Exception as e:
        logger.error(f"Error during query execution: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")



# Define a route to fetch data from the associate_info table and display as HTML
@app.get("/associates", response_class=HTMLResponse)
async def get_associates():
    async with pool.acquire() as conn:
        associates = await conn.fetch('SELECT * FROM associates_info ORDER BY id ASC')

        # Filter associates by department
        it_associates = [associate for associate in associates if associate['department'] == 'IT']
        marketing_associates = [associate for associate in associates if associate['department'] == 'Marketing']
        engineering_associates = [associate for associate in associates if associate['department'] == 'Engineering']

        html_content = """
        <html>
        <head>
            <title>Associates Information</title>
            <style>
                body { background-color: #DBDBDB; font-family: Arial, sans-serif; }
                .container { display: flex; flex-wrap: wrap; justify-content: space-between; }
                .top-container { display: flex; justify-content: space-between; width: 100%; margin-bottom: 20px; }
                .table-container { width: 45%; }
                .bottom-container { width: 100%; margin-top: 20px; text-align: center; }
                table { width: 100%; border-collapse: collapse; margin-bottom: 20px; }
                th, td { border: 1px solid black; padding: 8px; text-align: left; }
                th { background-color: lightgrey; }
                h2 { color: blue; font-style: italic; font-family: "Roboto", serif; font-weight: bold; text-decoration: underline; }
                .form-container { margin-top: 20px; }
                .form-container input[type=text], .form-container input[type=number], .form-container input[type=date] { padding: 10px; margin: 5px; }
                .form-container input[type=submit] { padding: 10px 20px; margin: 5px; background-color: #4CAF50; color: white; border: none; cursor: pointer; }
                .form-container input[type=submit]:hover { background-color: #45a049; }
                .home-button { display: inline-block; margin: 10px; padding: 10px 20px; background-color: #4CAF50; color: white; text-decoration: none; border-radius: 5px; }
                .home-button:hover { background-color: #45a049; }
            </style>
        </head>
        <body>
            <h1>Associates Information</h1>
            <div class="container">
                <div class="top-container">
                    <div class="table-container">
                        <h2>IT Department</h2>
                        <table>
                            <thead>
                                <tr>
                                    <th>ID</th>
                                    <th>Name</th>
                                    <th>Hire Date</th>
                                    <th>Manager</th>
                                </tr>
                            </thead>
                            <tbody>
        """

        for associate in it_associates:
            html_content += f"""
            <tr>
                <td>{associate['id']}</td>
                <td>{associate['name']}</td>
                <td>{associate['hire_date']}</td>
                <td>{associate['manager']}</td>
            </tr>
            """

        html_content += """
                            </tbody>
                        </table>
                    </div>
                    <div class="table-container">
                        <h2>Marketing Department</h2>
                        <table>
                            <thead>
                                <tr>
                                    <th>ID</th>
                                    <th>Name</th>
                                    <th>Hire Date</th>
                                    <th>Manager</th>
                                </tr>
                            </thead>
                            <tbody>
        """

        for associate in marketing_associates:
            html_content += f"""
            <tr>
                <td>{associate['id']}</td>
                <td>{associate['name']}</td>
                <td>{associate['hire_date']}</td>
                <td>{associate['manager']}</td>
            </tr>
            """

        html_content += """
                            </tbody>
                        </table>
                    </div>
                </div>
                <div class="bottom-container">
                    <h2>Engineering Department</h2>
                    <table>
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Name</th>
                                <th>Hire Date</th>
                                <th>Manager</th>
                            </tr>
                        </thead>
                        <tbody>
        """

        for associate in engineering_associates:
            html_content += f"""
            <tr>
                <td>{associate['id']}</td>
                <td>{associate['name']}</td>
                <td>{associate['hire_date']}</td>
                <td>{associate['manager']}</td>
            </tr>
            """

        html_content += """
                        </tbody>
                    </table>
                    <a href="/" class="home-button">Back to Home</a>
                </div>
            </div>
            <div class="form-container">
                <h2>Add Associate</h2>
                <form action="/associates" method="post">
                    <input type="text" name="name" placeholder="Enter Name" required>
                    <input type="date" name="hire_date" placeholder="Enter Hire Date" required>
                    <input type="text" name="manager" placeholder="Enter Manager" required>
                    <input type="text" name="department" placeholder="Enter Department" required>
                    <input type="submit" value="Add Associate">
                </form>
            </div>
            <div class="form-container">
                <h2>Delete Associate</h2>
                <form action="/delete_associate" method="post">
                    <input type="number" name="id" placeholder="Enter Associate ID" required>
                    <input type="submit" value="Delete Associate">
                </form>
            </div>
            <div class="form-container">
                <h2>Edit Associate</h2>
                <form action="/edit_associate" method="post">
                    <input type="number" name="id" placeholder="Enter Associate ID" required>
                    <input type="text" name="name" placeholder="Enter New Name">
                    <input type="date" name="hire_date" placeholder="Enter New Hire Date">
                    <input type="text" name="manager" placeholder="Enter New Manager">
                    <input type="text" name="department" placeholder="Enter New Department">
                    <input type="submit" value="Edit Associate">
                </form>
            </div>
        </body>
        </html>
        """
        return HTMLResponse(content=html_content)

## Endpoint to insert data into the database
@app.post("/associates", response_class=HTMLResponse)
async def insert_associate(
        name: str = Form(...),
        hire_date: str = Form(...),
        manager: str = Form(...),
        department: str = Form(...)
):
    try:
        hire_date_obj = datetime.strptime(hire_date, "%Y-%m-%d").date()  # Convert string to date object
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid hire date format. Please use YYYY-MM-DD format.")

    async with pool.acquire() as conn:
        try:
            await conn.execute('''
                INSERT INTO associates_info (name, hire_date, manager, department) 
                VALUES ($1, $2, $3, $4)
            ''', name, hire_date_obj, manager, department)
            # Redirect back to the /associates page after insertion
            return RedirectResponse("/associates", status_code=303)
        except asyncpg.exceptions.DataError:
            raise HTTPException(status_code=400, detail="Invalid data provided.")
# Define a route to delete associate data from the associate_info table
@app.post("/delete_associate")
async def delete_associate(id: int = Form(...)):
    async with pool.acquire() as conn:
        try:
            result = await conn.execute('DELETE FROM associates_info WHERE id = $1', id)
            if result == "DELETE 0":
                raise HTTPException(status_code=404, detail="Associate not found")
            return RedirectResponse(url="/associates", status_code=303)
        except Exception as e:
            logger.error(f"Error deleting associate: {e}")
            raise HTTPException(status_code=500, detail="Internal Server Error")

# Define a route to update associate data in the associate_info table
@app.post("/edit_associate")
async def edit_associate(id: int = Form(...), name: str = Form(None), hire_date: str = Form(None), manager: str = Form(None), department: str = Form(None)):
    if not any([name, hire_date, manager, department]):
        raise HTTPException(status_code=400, detail="At least one field must be provided to update")

    fields = []
    values = []

    if name:
        fields.append("name = $" + str(len(fields) + 2))
        values.append(name)
    if hire_date:
        fields.append("hire_date = $" + str(len(fields) + 2))
        values.append(hire_date)
    if manager:
        fields.append("manager = $" + str(len(fields) + 2))
        values.append(manager)
    if department:
        fields.append("department = $" + str(len(fields) + 2))
        values.append(department)

    query = "UPDATE associates_info SET " + ", ".join(fields) + " WHERE id = $1"

    logger.info(f"Executing query: {query} with values {[id] + values}")

    async with pool.acquire() as conn:
        try:
            result = await conn.execute(query, id, *values)
            if result == "UPDATE 0":
                raise HTTPException(status_code=404, detail="Associate not found")
            return RedirectResponse(url="/associates", status_code=303)
        except Exception as e:
            logger.error(f"Error updating associate: {e}")
            raise HTTPException(status_code=500, detail="Internal Server Error")

# Run the application
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
