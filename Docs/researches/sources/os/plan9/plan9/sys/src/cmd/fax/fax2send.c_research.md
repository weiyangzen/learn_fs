# File Research: sources/os/plan9/plan9/sys/src/cmd/fax/fax2send.c

Sends one or more fax page files through a Class 2 modem.

Key behavior:
- Initializes fax modem state and waits for initial `OK` after dialing.
- Enables XON/XOFF flow control through the modem control fd.
- Opens each fax page, sends geometry with `AT+FDT=...`, waits for `CONNECT`, and streams data.
- Doubles DLE bytes in outgoing page data.
- Polls modem input between buffers to handle CAN, XON, XOFF, and unexpected bytes.
- Ends each page with DLE ETX, waits for `OK`, sends `AT+FET`, and validates `FPTS`.

Important implementation details:
- Uses rough software flow-control timing for problematic modems.
- On error, disables flow control, closes the page `Biobuf`, sends `AT+FK`, and consumes a short response.
- Page counter advances across all input files.

Risks and invariants:
- Error label cleanup assumes `m->bp` is valid on paths after `openfaxfile()`.
- Modem-specific behavior is encoded in protocol timing and flow-control comments.
