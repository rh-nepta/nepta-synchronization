clean: 
	find . -type f -name "*.pyc" -exec rm -f {} \;
	find . -type d -name "__pycache__" -delete

run: 
	./runtest.sh

install:
	cp synchronization.service /usr/lib/systemd/system/nepta-synchronization.service
	systemctl daemon-reload
	systemctl enable --now nepta-synchronization.service
