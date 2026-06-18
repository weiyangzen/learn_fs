# File Research: sources/local-fs/ocfs2-tools/debugfs.ocfs2/include/commands.h

## Role

This header exposes the command dispatcher interface for `debugfs.ocfs2`.

## API

It declares:

- `do_command(char *cmd)` for parsing and executing one debugfs command line.
- `handle_signal(int sig)` for SIGTERM/SIGINT cleanup.

## Dependencies

The declarations are implemented in `commands.c` and used by `main.c`.
