# sources/sync-backup/git-crypt/util.cpp

Purpose: platform-neutral utility functions for subprocess execution, shell argument quoting, binary integer encoding, explicit memory clearing, constant-time comparison, and stream initialization.

Important APIs/types/functions: `exec_command`, `exec_command` with output capture, `exec_command_with_input`, `escape_shell_arg`, `load_be32`, `store_be32`, `read_be32`, `write_be32`, `explicit_memset`, `leakless_equals`, and `init_std_streams`.

Control flow: command helpers instantiate `Coprocess`, optionally attach stdout/stdin streams, spawn, stream all output or input, close stdin where needed, and wait. Encoding helpers read/write 32-bit big-endian values. `explicit_memset` writes via volatile pointer to avoid optimization. `leakless_equals` accumulates XOR differences across all bytes. Stream initialization disables iostream/stdio sync, unties cin, enables badbit exceptions, and calls platform-specific setup.

State/persistence behavior: subprocess helpers may cause external process side effects. Other utilities only mutate buffers or stream global settings. Platform-specific utilities are included at the bottom based on `_WIN32`.

Dependencies/integration: depends on `Coprocess`, `git-crypt.hpp` for platform utility inclusion needs, iostreams, and selected platform source. Used by nearly every subsystem.

Risks/test signals: `escape_shell_arg` is used for Git config command strings, so quoting semantics matter. `exec_command_with_input` can deadlock if a child writes enough stdout/stderr while input is being written because output is not drained concurrently. Tests should cover command output capture, input delivery, nonzero exit handling, big-endian round trips, constant-time compare behavior at API level, and binary stream mode on Windows.
