git add ./archivist/paywalled
git add ./data-daddy/data/server_messages.csv
git commit -m "stored files update"
git pull origin master
git push origin master

kill $(ps -ef | grep -v "grep" | grep -m 1 archivist.py | sed 's@^[^0-9]*\([0-9]\+\).*@\1@')
nohup python3 ./archivist/archivist.py &
kill $(ps -ef | grep -v "grep" | grep -m 1 data-daddy.py | sed 's@^[^0-9]*\([0-9]\+\).*@\1@')
nohup python3 ./data-daddy/data-daddy.py &
kill $(ps -ef | grep -v "grep" | grep -m 1 sportsballist.py | sed 's@^[^0-9]*\([0-9]\+\).*@\1@')
nohup python3 ./sportsballist/sportsballist.py &