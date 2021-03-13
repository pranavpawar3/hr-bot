Mongo Setup -- 

`sudo docker pull mongo`

`sudo docker run --name=mongodb_3 -v /home/pranav/docker_content/mongo_d/data:/data/db -p 27017:27017 -d mongo`

Accessible at port:27017, anywhere on the local network

Ngrock forwarding
sample command -- `ngrok http 4200 -host-header="localhost:4200"`

to redirect interrupted port again to its original link/ or any custom link -- `ngrok http 4200 -host-header="localhost:4200" -hostname=982269ff6871.ngrok.io`

1. rasa X - 5002
2. rasa actions server - 5055
3. MongoDB server - 27017
4. Doc upload server - 2000