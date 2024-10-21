
Photon Laser Tag Setup
Overview
This project is a Photon Laser Tag setup application that uses Tkinter for the graphical interface, UDP sockets for communication, and PostgreSQL for managing player data. The game allows for the entry and management of players across two teams, with broadcast capabilities for equipment IDs.


Step-by-Step Installation
Install Python 3.x: Download and install Python from the official website: https://www.python.org/downloads/

Install Required Python Packages:
socket
threading
random
psycopg2
sys
tkinter
Pillow


File Structure

project_root/
│
├── main.py               # Main application script
├── Images/
│   └── logo.jpg          # Logo image used for the splash screen
└── README.md             # This ReadMe file

main.py: The main script that contains all functionality (UI, UDP communication, database handling).
Images/: Contains the logo image (logo.jpg) used in the splash screen.

How to Run the Program
Run the main.py script:

python3 main.py


Optional: UDP_Listener.py 
This is for checking that the UDP messages are correctly sent.

The splash screen will appear, followed by the main window where you can enter player data for two teams, view the player database, and press enter for each team member to submit ID, Codename, and Equipment ID Initialization over UDP broadcast.

For the F5 key functionality, press 's' instead to accomplish the abilities because the F5 key does not work efficiently. Professor strother allows this as he allows the F12 key to be esc instead.


| Real Name             | GitHub Username |
|-----------------------|-----------------|
| Lauren Greer Robinson | greerrobinson   |
| Paul Tribble          | paultribble     |
| Adel Barbarawi        | Adel-Barbarawi  |
| Dakota Stokes         | dakotalstokes   |
| Brooke Avant          | brookeavant5    |
