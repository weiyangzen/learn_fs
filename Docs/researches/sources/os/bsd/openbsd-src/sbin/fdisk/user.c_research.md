# File Research: sources/os/bsd/openbsd-src/sbin/fdisk/user.c

Implements fdisk’s interactive command loop and top-level disk printing.

Core behavior:
- Defines the interactive command table: `help`, `manual`, `reinit`, `setpid`, `edit`, `flag`, `update`, `select`, `swap`, `print`, `write`, `exit`, `quit`, and `abort`.
- Tracks whether the current edit level has uncommitted changes with global `modified`.
- `USER_edit` reads the current MBR, loads GPT state on the outer edit level, prompts as `<disk>[*]: <level>`, dispatches commands, and handles clean/dirty/exit/quit status returns.
- Recursive edit levels are used for extended MBRs; GPT reinitialization unwinds nested MBR editing.
- `USER_print_disk` prints primary/secondary GPT state when present, then walks the MBR and any extended MBR chain.
- `USER_help` filters commands by partition table validity and GPT context.
- `ask_cmd` parses one command line, supports `?` as `help`, accepts command prefixes, and rejects unavailable or ambiguous context-inappropriate commands.

This is the user interaction layer that connects parsed commands to the lower-level MBR/GPT editing functions.
