# File Research: sources/os/plan9/plan9/sys/src/cmd/fax/modem.h

Shared fax modem interface and state definition.

Key contents:
- `Modem` structure for modem fds, response/error buffers, fax session state, page file state, input buffering, `Biobuf` page input, and negotiated FDCS parameters.
- Result code enum for modem responses.
- Error code enum for user-facing retry/protocol/system states.
- Valid-bit enum for page responses and opened file metadata.
- Function prototypes across fax modem parsing, receive, send, file handling, modem I/O, and logging helpers.

Important relationships:
- `valid` is a bitmask spanning modem responses (`Vfdcs`, `Vftsi`, `Vfpts`, `Vfet`, `Vfhng`) and file metadata (`Vwd`, `Vtype`).
- `fax2send.c` and `fax2receive.c` share the same `Modem` state and error reporting.
