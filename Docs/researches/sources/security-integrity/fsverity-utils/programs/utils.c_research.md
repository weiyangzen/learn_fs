# sources/security-integrity/fsverity-utils/programs/utils.c

Purpose: This file implements shared CLI utilities for error reporting, safe allocation, file open/close wrappers, full reads/writes, file size queries, hex parsing/printing, and tree parameter parsing.

Important APIs and functions: It provides `error_msg`, `error_msg_errno`, `xzalloc`/`xmalloc`, `open_file`, `filedes_close`, `full_read`, `full_write`, `get_file_size`, salt/hex helpers, hash-alg/block-size parsing, and common `parse_tree_param` behavior.

Control flow and state: Helpers maintain small resource state in `struct filedes` and otherwise operate statelessly. Full I/O helpers loop until requested bytes are processed or errors occur.

Dependencies and integration points: Used by all CLI subcommands and test utilities. It bridges libc file descriptors, libfsverity public params, and user-facing diagnostics.

Risks and test signals: Risks include partial I/O handling, numeric overflow, duplicate/invalid option reporting, and file descriptor cleanup. Signals are CLI tests for malformed options, full binary stdout writes, and reliable cleanup on errors.
