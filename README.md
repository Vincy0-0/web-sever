Project Structure
This repository follows the required submission structure:
* `src/server.py`: The main multi-threaded Python web server.
* `test_files/`: Directory containing HTML and image files for GET/HEAD testing.
* `server.log`: Log file tracking all client requests and server responses.
* `README.md`: Compilation and execution instructions.

Prerequisites
* Python 3.x installed.
* Standard libraries only (`socket`, `threading`, `os`, etc.).

How to Compile and Run
1. Open a terminal and navigate to the root of the repository (`web-server/`).
2. Run the server by targeting the script inside the src folder:
   ```bash
   python src/server.py
3. Open the link in PORTS or copy it into the browser
4. Add /index.html at the end of the link when its not working for the text file
5. Add no_study.JPG at the end of the link when its not working for the image file
