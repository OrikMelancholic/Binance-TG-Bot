import asyncio
import threading
import websockets
import json


class WebSocket(threading.Thread):
    def __init__(self, websocket_url, bot):
        super().__init__()
        self.url = websocket_url
        self._loop = asyncio.new_event_loop()
        self._tasks = {}
        self._stop_event = None
        self.ws = None
        self.bot = bot

    def run(self):
        print("Запуск потока вебсокета...")
        self._stop_event = asyncio.Event()

        try:
            self._loop.run_until_complete(self._stop_event.wait())
            self._loop.run_until_complete(self._clean())
        finally:
            self._loop.close()

    def stop(self):
        self._loop.call_soon_threadsafe(self._stop_event.set)

    def connect(self):
        def _connect():
            if self.url not in self._tasks:
                task = self._loop.create_task(self._listen())
                self._tasks[self.url] = task
        self._loop.call_soon_threadsafe(_connect)

    def disconnect(self):
        def _disconnect():
            task = self._tasks.pop(self.url, None)
            if task is not None:
                task.cancel()
        self._loop.call_soon_threadsafe(_disconnect)

    async def _listen(self):
        try:
            while not self._stop_event.is_set():
                try:
                    ws = await websockets.connect(self.url, loop=self._loop)
                    while ws.open:
                        packet = await ws.recv()
                        packet = json.loads(packet)
                        print('Получено от сервера: ', packet)
                        msg = 'Валюта %s прошла цель в %s$ с курсом %s$ (%s)' % (
                            packet['flair'], packet['target'], packet['price'],
                            'рост' if packet['rising'] else 'падение'
                        )
                        self.bot.send_message(chat_id=packet['user_id'], text=msg)
                except Exception as e:
                    print('Отловлена ошибка, перезапускаю вебсокет...\n', e)
                    await asyncio.sleep(2)

        finally:
            self._tasks.pop(self.url, None)

    async def _clean(self):
        for task in self._tasks.values():
            task.cancel()
        await asyncio.gather(*self._tasks.values(), loop=self._loop)
