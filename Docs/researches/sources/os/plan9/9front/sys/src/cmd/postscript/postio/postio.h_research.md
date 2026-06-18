# File Research: sources/os/plan9/9front/sys/src/cmd/postscript/postio/postio.h

`postio.h` defines constants, status mappings, baud mappings, buffer sizes, and function declarations for `postio.c` and `slowsend.c`.

Key definitions:
- `POSTBEGIN` defaults to PostScript code disabling job timeouts.
- Connection states: `NOTCONNECTED`, `START`, `SEND`, `DONE`.
- Process role flags: `READ`, `WRITE`, `READWRITE`.
- Printer status codes: `BUSY`, `WAITING`, `PRINTING`, `IDLE`, `ENDOFJOB`, `PRINTERERROR`, `ERROR`, `FLUSHING`, `INITIALIZING`, `DISCONNECT`, `UNKNOWN`, `NOSTATUS`, plus pseudo-states `WRITEPROCESS` and `INTERACTIVE`.
- `Status` struct and `STATUS` initializer map lower-case status strings to status codes.
- `BAUDRATE` defaults to `B9600`.
- `Baud` struct and `BAUDTABLE` map strings such as `9600`, `19200`, `19.2`, `38400`, etc. to tty baud constants.
- `BLOCKSIZE=2048` and `MESGSIZE=512`.
- Declares non-integer functions `find()`, `malloc()`, and `strtok()`.

This header encodes most of `postio`’s protocol vocabulary and default runtime parameters.
