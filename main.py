from pywebio import start_server
from pywebio.input import *
from pywebio.output import *
from pywebio.session import run_async, run_js

import http.client
import asyncio


chat_msgs = []
online_users = set()

MAX_MESSAGES_COUNT = 100

async def main():
    global chat_msgs
    
    put_markdown("##Hello, this my small chat, connect faster))##")

    msg_box = output()
    put_scrollable(msg_box, height=300, keep_bottom=True)
    
    nickname = await input("Enter to chat", required=True, placeholder="Your name", validate=lambda n: "This nick has been used" if n in online_users or n == '🔈' else None)
    online_users.add(nickname)
    
    user_ip = get_user_ip()
    
    chat_msgs.append(('🔈', f"'{nickname}' joined!"))
    msg_box.append(put_markdown((f"'{nickname}' joined!")))

    refresh_task = run_async(refresh_msg(nickname, msg_box))
    
    while True:
        data = await input_group("New message!", [
            input(placeholder="Text", name="msg"),
            actions(name="cmd", buttons=["Send", {'label':"Exit from chat", 'type':'cancel'}])
        ], validate=lambda m: ('msg', "Enter the text!") if m["cmd"] == "Send" and not m["msg"] else None)
        
        print(f"'{nickname}': {data['msg']} |||| ip: {user_ip}")
        
        if data is None:
            break
        
        msg_box.append(put_markdown(f"'{nickname}': {data['msg']}"))
        chat_msgs.append((nickname, data['msg']))
        
    # exit chat
    refresh_task.close()
    
    online_users.remove(nickname)
    toast("Your leave from chat!")
    msg_box.append(put_markdown(f"🔈 User '{nickname}' leave from us!"))
    chat_msgs.append(('🔈', f"User '{nickname}' leave from us!"))
    
    put_buttons(["Reconnect"], onclick=lambda btn: run_js('window.location.reload()'))
    
    
async def refresh_msg(nickname, msg_box):
    global chat_msgs
    last_idx = len(chat_msgs)
    
    while True:
        await asyncio.sleep(1)
        
        for m in chat_msgs[last_idx:]:
            if m[0] != nickname:
                msg_box.append(put_markdown(f"'{m[0]}': {m[1]}"))
                
        #remove expired
        if len(chat_msgs) > MAX_MESSAGES_COUNT:
            chat_msgs = chat_msgs[len(chat_msgs) // 2:]
            
        last_idx = len(chat_msgs)


def get_user_ip():
    conn = http.client.HTTPConnection("ifconfig.me")
    conn.request("GET", "/ip")
    return conn.getresponse().read()

if __name__ == "__main__":
    start_server(main, debug=True, port=8080, cdn=False)