
import os
import json
import asyncio
import websockets

async def handle_task(ws):
    try:
        task = json.loads(await ws.recv())
        await ws.send(json.dumps({
            "type": "done",
            "final_message": "Python harness started. "
                             "Model integration still requires "
                             "the official evaluator credentials."
        }))
    except Exception as e:
        await ws.send(json.dumps({
            "type": "error",
            "message": str(e)
        }))

async def main():
    async with websockets.serve(
        handle_task, "0.0.0.0",
        int(os.environ.get("PORT", "8765"))
    ):
        print("Engineering Agent running")
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
