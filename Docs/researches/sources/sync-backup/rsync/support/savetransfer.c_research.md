<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/support/savetransfer.c -->
# sources/sync-backup/rsync/support/savetransfer.c

Purpose: C proxy helper that runs a program while copying stdin to stdout and saving either the data going into the program or coming out of it. It is used to inspect rsync protocol streams through remote-shell paths.

Important APIs/types/functions: `main()`, `run_program()`, `set_nonblocking()`, and `set_blocking()`. Global state includes `buf[4096]` and `save_data_from_program`.

Control flow: parse `-i` or `-o`, open/truncate the output file in binary mode, ignore `SIGPIPE`, fork/exec the requested program with one side of a pipe connected to its stdin or stdout, put stdio into binary mode where needed, set stdin nonblocking and stdout blocking, then loop with a 30-second `select()` timeout reading stdin, writing the same bytes to stdout and the capture file. Timeout or EOF ends the loop.

State and persistence behavior: creates or truncates the capture file and proxies bytes between process descriptors. It does not wait for the child explicitly, so process lifetime is mostly governed by pipe closure and exec behavior.

Dependencies and integration points: includes `../rsync.h` for portability macros such as `NONBLOCK_FLAG`, `O_BINARY`, `SIGACTION`, and platform headers. It integrates with rsync examples via `--rsh` and `--rsync-path`.

Risks: the 30-second inactivity timeout is a hard-coded behavior that can delay completion or abort slow transfers. Partial writes are treated as fatal rather than retried. It may not notice child exit promptly when saving input and no more data arrives. Capture files can contain sensitive protocol/data bytes.

Test signals: run with simple producer/consumer commands in both `-i` and `-o` modes, verify captured streams match expected data, binary bytes are preserved, timeout behavior is understood, and failed exec/pipe/write paths report errors.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/support/savetransfer.c -->
