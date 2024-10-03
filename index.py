import MetaTrader5 as mt5
import websockets
import asyncio
import json

LOGIN = 86861371 
PASSWORD = "Y+UgNtN2" 
SERVER = "MetaQuotes-Demo" 

# تنظیمات API متاتریدر
def initialize_mt5():
    # شروع متاتریدر
    print("Initializing MetaTrader5...")
    if not mt5.initialize():
        print("Failed to initialize MetaTrader5")
        return False

    # اتصال به حساب
    print("Logging into MetaTrader5 account...")
    authorized = mt5.login(LOGIN, password=PASSWORD, server=SERVER)
    if not authorized:
        print(f"Failed to login to MetaTrader5. Error code: {mt5.last_error()}")
        return False

    print("Connected to MetaTrader5")
    return True

def get_account_info():
    account_info = mt5.account_info()
    if account_info is None:
        print("Failed to retrieve account info")
        return None
    return {
        "balance": account_info.balance,
        "equity": account_info.equity,
        "margin_level": account_info.margin_level,
    }

def get_open_trades():
    trades = mt5.positions_get()
    if trades is None:
        print("Failed to retrieve trades")
        return []
    return [{"symbol": trade.symbol, "volume": trade.volume, "price_open": trade.price_open} for trade in trades]

# سرور وب‌سوکت
async def socket_server(websocket, path):
    print("Starting WebSocket server...")

    if not initialize_mt5():
        await websocket.send(json.dumps({"error": "Failed to initialize MetaTrader5"}))
        return

    print("WebSocket server started. Waiting for client connections...")

    while True:
        account_info = get_account_info()
        open_trades = get_open_trades()

        if account_info and open_trades is not None:
            data = {
                "account_info": account_info,
                "open_trades": open_trades,
            }
            print(f"Sending data to client: {data}")
            await websocket.send(json.dumps(data))

# اجرای سرور
async def start_server():
    print("Initializing WebSocket server...")
    async with websockets.serve(socket_server, "localhost", 8765):
        print("WebSocket server is running on ws://localhost:8765")
        await asyncio.Future()  # نگه‌داشتن سرور

# اجرای سرور به صورت غیرهمزمان
asyncio.run(start_server())