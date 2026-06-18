# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/cifscmd.c

Interactive SMB client command tool focused on testing remote operations.

Key functions:
- `tokenise` and `parse` split command lines, including single-quoted strings and doubled embedded quotes.
- `cmdhelp` prints command help.
- `cmdopen` maps textual share/open modes and calls `smbclientopen`.
- `threadmain` optionally connects to a server/share, reads commands from stdin, dispatches them, and writes status to stdout.

Interactions:
- Uses `smbconnect` for connection setup and `smbclientopen` for file open testing.
- Uses local mode lookup tables similar to server-side `smbopenmodeslut` and `smbsharemodeslut`.

Notable details:
- Currently exposes only `help` and `open`.
- Prints parsed argument count unconditionally through `Bprint`.
