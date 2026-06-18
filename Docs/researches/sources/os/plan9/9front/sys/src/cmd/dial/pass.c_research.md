# File Research: sources/os/plan9/9front/sys/src/cmd/dial/pass.c

Purpose: Bidirectional line-oriented pass-through between `/dev/cons` and stdin/stdout, useful for dialing scripts that need user input.

Key behavior:
- Option: `-q` suppress echoing received stdin data to console.
- Opens `/dev/cons` and tries to set raw mode through `/dev/consctl`.
- Forks shared-memory processes:
  - parent reads stdin and optionally echoes to console until done or newline/carriage return,
  - child reads one character at a time from console, writes to stdout, and stops at newline/carriage return.
- Uses a 250 ms alarm loop to let the reader notice shared `done`.

Notable details:
- Shared `done` and `alarmed` depend on `RFMEM`.
