# File Research: sources/os/plan9/plan9/sys/src/cmd/fax/modem.c

Low-level modem command, input buffering, response parsing, and flow-control helpers for fax tools.

Key behavior:
- Defines a response table mapping terse/verbose modem strings to result codes and optional fax response handlers.
- `initmodem()` stores data fd, control fd, type, and local id.
- `rawmchar()` reads buffered modem bytes, using `dirfstat()` length to avoid blocking when no bytes are ready.
- `getmchar()` waits for a single byte with timeout.
- `getmline()` reads CRLF-terminated response lines while ignoring XON/XOFF bytes.
- `command()` writes AT commands with carriage return.
- `response()` reads lines until one matches the result table, invoking fax-specific handlers when needed.
- `xonoff()` writes `x0` or `x1` to the control fd.

Important implementation details:
- Response matching is prefix-based against verbose strings.
- Fax status lines such as `+FPTS` can be consumed as intermediate `Rcontinue` events until a final response appears.

Risks and invariants:
- `response()` returns `Rnoise` on timeout or unmatched input after clearing the response buffer.
- `rawmchar()` depends on modem fd directory length semantics.
