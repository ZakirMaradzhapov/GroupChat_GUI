# GroupChat description
I created a chat server that accepts several connections from chat clients. The idea
is to create a chat conference where users send broadcast messages (one-to-all, kind of
WhatsApp group). When a user sends a message the user name should appear next to the
message. You can consider that usernames are all unique. 
Server saves the log of all the incoming messages in a database in case if a user asks for 
the log of his/her messages. 

There is a possibility for users to send private messages to each other. It is done this way: 
On client side sending message: /private to username_here message_content. If private message 
is sent, only destination user gets its content (sender of the letter is also noted)
