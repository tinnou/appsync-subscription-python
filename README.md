# appsync-subscription-python
AppSync subscription registration and connection in python

## Getting Started

This snippet uses the Sample Event App in the console. Create an API using that sample.
Execute a mutation to create an event.
Grab API url, API key and event id that was just created and replace them inside the snippet.
Run the snippet using `python3 appsync-subscribe.py`, it will register a subcription listening for comments on that event.
Execute a createComment mutation in the console and you should see the comment flowing through the websocket.
