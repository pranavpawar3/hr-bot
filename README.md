Mongo Setup -- 

`sudo docker pull mongo`

`sudo docker run --name=mongodb_3 -v /home/pranav/docker_content/mongo_d/data:/data/db -p 27017:27017 -d mongo`

Its accessible at port:27017, anywhere on the local network

<!-- sample command -- `ngrok http 4200 -host-header="localhost:4200"`

to redirect interrupted port again to its original link/ or any custom link -- `ngrok http 4200 -host-header="localhost:4200" -hostname=982269ff6871.ngrok.io` -->

Ngrock forwarding
add the ports to $HOME/.ngrok2/ngrok.yml (/home/pranav/.ngrok2/ngrok.yml)
ngrok start --all
1. rasa X - 5002 - http://rasax-teamfriendsofhr.ngrok.io/
    rasa X password: "showmethebot"
    it needs to be exported as an ENV variable, before executing `rasa x`
2. rasa actions server - 5055 - http://actions-teamfriendsofhr.ngrok.io/
3. MongoDB server - 27017 - tcp://2.tcp.ngrok.io:14374
4. Doc upload server - 2000 - https://doc-teamfriendsofhr.ngrok.io/

