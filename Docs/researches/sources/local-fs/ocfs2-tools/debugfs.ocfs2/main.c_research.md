# File Research: sources/local-fs/ocfs2-tools/debugfs.ocfs2/main.c

## Role

`main.c` is the process entry point for `debugfs.ocfs2`. It parses top-level options, initializes error tables and signals, handles special modes, opens an optional device, and runs command-file or interactive command execution.

## Top-Level Modes

It supports:

- Trace/log mask mode with `-l`.
- Lockname decode mode with `-d`/`--decode`.
- Lockname encode mode with `-e`/`--encode`.
- Normal debugfs command mode with optional device, `-f` command file, `-R` one-shot command, `-i` image mode, `-s` backup superblock, `-w` write mode, and `-n` no prompt.

## Command Loop

For normal mode, it optionally synthesizes an `open` command for the requested device, executes one-shot commands, opens command files, prints version unless prompt is disabled, then reads commands from the file or readline and passes them to `do_command()`.

## Log Control

It can read or set OCFS2/o2cb trace masks through newer sysfs paths, older sysfs paths, or the legacy proc file.

## Risk Areas

The long-option table maps `"write"` to `'?'` instead of `'w'`, so long `--write` follows the help/version path while short `-w` works. The program uses global state, signal-triggered cleanup, and simple command-line parsing.
