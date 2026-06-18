# File Research: sources/local-fs/jfsutils/fscklog/fscklog.c

Main program for `jfs_fscklog`, coordinating command-line parsing, extraction, display, and message output.

Key contents:
- Documents usage: `jfs_fscklog [-d] [-e <device>] [-f <file.name>] [-p] [-V]`.
- Global state includes `fscklog_record`, `local_recptr`, `file_name[128]`, `Vol_Label`, and booleans `extract_log`/`display_log`.
- `main()` prints version/date, initializes state, parses arguments, then calls `xchklog()` for extraction and `xchkdmp()` for display if requested.
- `parse_parms()` handles:
  - `-d` display already extracted log.
  - `-e device` extract from device and verifies path can be opened.
  - `-f file.name` sets input/output file name, with a length check.
  - `-p` selects old/prior log.
  - `-V` exits after version output.
- `fscklog_usage()` prints emergency help.
- `v_send_msg()` formats a message from `msg_defs`, appends `[file:line]` detail, and prints both.

Interactions:
- Includes `jfs_version.h`, `jfs_fscklog.h`, `xfsck.h`, and fsck message definitions.
- Delegates real work to `extract.c` and `display.c`.

Research notes:
- File-name length check accepts `arg_len > 128`, but `file_name` is 128 bytes and `strncpy(file_name, optarg, arg_len)` does not append a terminator; exact 128-byte names are risky.
- `printf(msg_string)` in `v_send_msg()` prints formatted message text as a format string.
