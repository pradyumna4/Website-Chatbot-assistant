from bot_core import respond

print("Welcome to assistbot (type 'exit' to quit)")
while True:
    user_input = input("You: ")
    if user_input.lower() == 'exit':
        break
    bot_reply = respond(user_input)
    print("Bot:", bot_reply)

