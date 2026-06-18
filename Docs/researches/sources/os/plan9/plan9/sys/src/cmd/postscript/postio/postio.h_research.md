# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/postio/postio.h

Constants, state codes, and lookup-table definitions for `postio`.

Contents:
- Defines default `POSTBEGIN` PostScript sent before jobs: disables printer job timeout.
- Defines high-level connection states: `NOTCONNECTED`, `START`, `SEND`, `DONE`.
- Defines process role flags: `READ`, `WRITE`, `READWRITE`.
- Defines printer status codes: `BUSY`, `WAITING`, `PRINTING`, `IDLE`, `ENDOFJOB`, `PRINTERERROR`, `ERROR`, `FLUSHING`, `INITIALIZING`, `DISCONNECT`, `UNKNOWN`, `NOSTATUS`, plus dummy states `WRITEPROCESS` and `INTERACTIVE`.
- Defines `Status` and `STATUS` initializer mapping lowercase status strings to status codes.
- Defines default baud rate `BAUDRATE=B9600`.
- Defines `Baud` and `BAUDTABLE` mapping strings like `9600`, `19200`, `38.4`, `EXTB` to terminal speed constants.
- Defines `BLOCKSIZE=2048` and `MESGSIZE=512`.
- Declares `find()`, `malloc()`, and `strtok()`.

Role:
- Provides the shared protocol between option parsing, status parsing, send/done control flow, and platform I/O code.

Risks and quirks:
- Baud table assumes legacy speed constants `EXTA`/`EXTB`.
- Status recognition depends on lowercase strings and ordering before the `NULL` terminator.
- Function declarations are pre-ANSI and incomplete by modern C standards.
