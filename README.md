# cdpget

`cdpget` is a Python script that connects to a remote target via [Chrome DevTools Protocol](https://chromedevtools.github.io/devtools-protocol/) and prints the content of the provided file or directory.
This is achieved by navigation to the file using a file:// link, printing the page to pdf and reading the pdf's text content.

## Requirements

The script requires the following Python packages:

- `Requests`
- `websocket_client`
- `PyPDF2`

You can install these packages using pip:

```sh
pip install -r requirements.txt
```

## Usage

You can run the script with the following command:

```sh
python3 cdpget.py <file> [-v] [-t <target>] [-p <port>]
```

Where:

- `<file>` is the remote file to print.
- `-v` or `--verbose` enables verbose mode.
- `-t` or `--target` specifies the target to connect to (default is `127.0.0.1`).
- `-p` or `--port` specifies the port to use (default is `9222`).

## Example

```sh
python3 cdpget.py /root/.ssh/id_rsa -p 34242
```

This command will connect to the target at `127.0.0.1` on port `34242`, retrieve the file at `/root/.ssh/id_rsa` and print its content to the console.
