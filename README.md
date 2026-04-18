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

Testing Commands
**1. Test 200 OK (Success for Text and Images)**
Requesting an HTML file:
    curl -i http://127.0.0.1:8080/index.html

Requesting an Image file:
    curl -i http://127.0.0.1:8080/poly_logo.png

**2. Test 404 Not Found (Missing File)**
    curl -i http://127.0.0.1:8080/nonexistent_file.html

**3. Test 403 Forbidden (Directory Traversal Prevention)**
    curl -i --path-as-is http://127.0.0.1:8080/../src/server.py

**4. Test 304 Not Modified (Caching via If-Modified-Since)**
    curl -i -H "If-Modified-Since: Wed, 01 Jan 2030 00:00:00 GMT" http://127.0.0.1:8080/index.html

**5. Test 400 Bad Request (Unsupported Command)**
    curl -i -X INVALID http://127.0.0.1:8080/index.html

**Testing the HEAD Command**
    curl -I http://127.0.0.1:8080/index.html