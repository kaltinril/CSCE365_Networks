Everything in phase 1 should be implemented.

How to Use:
Start receiver and then sender.

python3 receiver.py -p 5000

python3 sender.py -f myfiletosend.txt -a localhost -p 5000 -e 10



receiver optionally can be supplied a filename to save the file as. 
(It was not specified in the assigmnet how you wanted this)

python3 receiver.py -f mysavedfile.txt -p 5000