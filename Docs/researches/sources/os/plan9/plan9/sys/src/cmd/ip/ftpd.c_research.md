# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/ftpd.c

`ftpd.c` is a Plan 9 FTP daemon.

Key behavior:
- Parses FTP commands from stdin, strips CR/LF, handles telnet IAC prefixes and a GatorFTP delimiter quirk, dispatches through `cmdtab`.
- Supports anonymous/none-only modes, debug logging, namespace selection, and auth via Plan 9 challenge/response or noworld login.
- Maintains current directory, transfer type/mode/structure, active/passive data address, restart offset, and transfer child pid.
- Implements login (`USER`/`PASS`), directory navigation (`PWD`, `CWD`, `CDUP`), type/mode/structure, active `PORT`, passive `PASV`, listings (`LIST`, `NLST`), file metadata (`SIZE`, `MDTM`), restart (`REST`), retrieve/store/append/unique store, mkdir/delete, abort, system/help, rename, and `SITE CHMOD`.
- `transfer` runs external commands such as `/bin/tar` through a pipe for directory retrieval.
- `list` implements Unix-style FTP listing output using Plan 9 `Dir` metadata and globbing.
- `retrieve` and `store` perform data connection I/O, converting LF/CRLF for ASCII mode and requiring image mode for high-bit data.
- `abspath` cleans paths, strips shell-special characters, and enforces `.httplogin` access restrictions via cached recursive checks.
- `dialdata` temporarily binds the right network namespace and supports active or passive data connections.

Important dependencies:
- Uses Plan 9 auth, namespace, netconninfo, String, glob, syslog, and process-note APIs.

Notable risks/quirks:
- Plain FTP plus legacy Plan 9 auth behavior; no modern FTP TLS path in this file.
- Anonymous uploads are restricted to `/incoming/`.
- Path sanitization truncates at special characters rather than rejecting the command.
