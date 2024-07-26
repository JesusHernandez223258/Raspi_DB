from fastapi import FastAPI
from fastapi_socketio import SocketManager
from src.controllers import auth_controller, user_controller
from src.middlewares.cors_middleware import add as add_cors_middleware
import threading
from src.services.serial_to_rabbit import main as serial_to_rabbit_main

app = FastAPI()
socket_manager = SocketManager(app=app)

# Agregar middlewares
add_cors_middleware(app)

# Incluir rutas de los controladores
app.include_router(auth_controller.router)
app.include_router(user_controller.router)

# Importar manejadores de eventos de socket
import src.socket_handlers

# Iniciar la lectura del serial en un hilo separado
serial_thread = threading.Thread(target=serial_to_rabbit_main)
serial_thread.daemon = True
serial_thread.start()

if __name__ == '__main__':
    import logging
    import sys
    import uvicorn

    logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)

    uvicorn.run(app, host='localhost', port=8000)
