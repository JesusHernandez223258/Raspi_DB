from fastapi_socketio import SocketManager
from src.main import socket_manager

@socket_manager.on('join')
async def handle_join(sid, *args, **kwargs):
    await socket_manager.emit('lobby', 'User joined')

@socket_manager.on('test')
async def test(sid, *args, **kwargs):
    await socket_manager.emit('hey', 'joe')
