# File Research: sources/os/plan9/plan9/sys/src/9/boot/getpasswd.c

Raw console password prompt.

Key behavior:
- Opens `#c/consctl` and enables raw mode.
- Prompts `password: ` and reads one byte at a time.
- Handles newline to finish, backspace to delete, and Ctrl-U to restart prompt.
- Does not echo password characters.
- Fatal-errors if console control/read fails.

Used by boot authentication/key flows.
