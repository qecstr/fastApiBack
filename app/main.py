import asyncio
import json
import time
import random
from fastapi.responses import HTMLResponse
import sqlalchemy as sql
from fastapi import FastAPI, Depends, WebSocket, WebSocketDisconnect
from fastapi.openapi.models import Response

from pydantic import BaseModel


import app.Models as Models
from typing import Annotated
from app.database import engine, SessionLocal
from sqlalchemy.orm import Session
import datetime
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

app = FastAPI()
Models.Base.metadata.create_all(bind=engine)
finances = sql.Table('Finances', sql.MetaData(), autoload_with=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=['GET','POST','DELETE'],
    allow_headers=["*"],
)
class Finances(BaseModel):
    date: datetime.date
    operation_type: str
    sum: float
    sender: str
    comment: str



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


@app.post("/finances")
async def create_finances(Finances: Finances, db: db_dependency):
    db_Finances = Models.Finances(date=Finances.date, operation_type=Finances.operation_type, sum=Finances.sum,
                                  sender=Finances.sender,
                                  comment=Finances.comment)
    db.add(db_Finances)
    db.commit()
    db.refresh(db_Finances)
    return  db.query(Models.Finances).filter(Models.Finances.date == Finances.date,
                                             Models.Finances.operation_type == Finances.operation_type,
                                             Models.Finances.sum == Finances.sum,
                                             Models.Finances.sender == Finances.sender,
                                             Models.Finances.comment == Finances.comment
                                             ).first()


@app.get("/finances/{id}")
async def get(id: int, db: db_dependency):
   
    query = db.query(Models.Finances).filter(Models.Finances.id == id).first()
    return query


@app.get("/financesAll")
async def getAll(db: db_dependency):
    query = db.query(Models.Finances).all()
    return query
@app.post("/financeUpdate/{id}")
async def update(Finances: Finances ,db :db_dependency,id:int ):

    query = db.query(Models.Finances).filter(Models.Finances.id == id).first()
    query.date=Finances.date
    query.operation_type = Finances.operation_type
    query.sum = Finances.sum
    query.sender = Finances.sender
    query.comment = Finances.comment
    db.commit()
    db.refresh(query)

@app.delete("/financesDelete/{id}")
async def delete(db: db_dependency,id:int ):
    query = db.query(Models.Finances).filter(Models.Finances.id == id).first()
    db.delete(query)
    db.commit()






































html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WebSocket Chart Example</title>
    <!-- Include Chart.js library -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <h1>WebSocket Chart Example</h1>
    <!-- Create a canvas element for the chart -->
    <canvas id="myChart" width="400" height="200"></canvas>

    <script>
        // Initialize WebSocket connection
        const socket = new WebSocket("ws://localhost:8000/ws");
        
        // Create a Chart.js chart
        const ctx = document.getElementById("myChart").getContext("2d");
        const myChart = new Chart(ctx, {
            type: "line",
            data: {
                datasets: [{
                    label: "Finances",
                    data: [],
                    backgroundColor: "rgba(255, 99, 132, 0.2)",
                    borderColor: "rgba(255, 99, 132, 1)",
                    borderWidth: 1,
                    fill: false
                }]
            },
            options: {
                scales: {
                    xAxes: [{
                        type: "time",
                          // Start from the right side
                        time: {
                            unit: "second", // Adjust time unit as needed
                            displayFormats: {
                                second: "MMM D HH:mm:ss" // Format datetime as needed
                            }
                            
                        }
                    }],
                    yAxes: [{
                        ticks: {
                            beginAtZero: true
                        }
                    }]
                }
            }
        });
        function generateTimestamp() {
            return new Date().toISOString(); // Generate current timestamp in ISO format
        }
        // WebSocket event listener for incoming data
        socket.addEventListener("message", function(event) {
            const data = JSON.parse(event.data);
            const timestamp = generateTimestamp();  // Assuming server sends timestamp
            const value = data.sum; // Parse value as a double
            console.log(timestamp);
            console.log(value);
            // Add data to the chart
            myChart.data.datasets[0].data.unshift({ x: timestamp, y: value });

            // Update the chart
            myChart.update();
            if (myChart.data.datasets[0].data.length > 10) {
                myChart.data.datasets[0].data.shift();
            }
        });
    </script>
</body>
</html>
"""




class ConnectionManager:
        def __init__(self):
            self.active_connections: list[WebSocket] = []

        async def connect(self, websocket: WebSocket):
            await websocket.accept()
            self.active_connections.append(websocket)

        def disconnect(self, websocket: WebSocket):
            self.active_connections.remove(websocket)

        async def broadcast(self,finances:Models.Finances):
            for connection in self.active_connections:
                timestamp = datetime.datetime.now().isoformat()
                await connection.send_json({"date":timestamp ,"sum":finances.sum})

manager = ConnectionManager()





@app.get("/html")
async def get():
    return HTMLResponse(html)
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket,db:db_dependency):
    await manager.connect(websocket)
    i=7
    while True:
        finances = getById(i,db)
        if finances is None:
            manager.disconnect(websocket)
            return
        await manager.broadcast(finances)
        i = i + 1
        await asyncio.sleep(1)



def getById(id:int,db:Session):
    query = db.query(Models.Finances).filter(Models.Finances.id == id).first()
    return query