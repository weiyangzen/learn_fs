# sources/sync-backup/git-crypt/util.hpp

Purpose: declares common utility and platform abstraction APIs for git-crypt.

Important APIs/types/functions: `struct System_error`, `class temp_fstream`, filesystem helpers `mkdir_parent`, `touch_file`, `remove_file`, `create_protected_file`, `util_rename`, `get_directory_contents`, process helpers `exec_command`, `exec_command_with_input`, `exit_status`, `successful_exit`, stream initialization, shell quoting, big-endian helpers, `explicit_memset`, and `leakless_equals`.

Control flow: no direct implementation flow; this header defines contracts shared by commands, crypto, key handling, GPG, and process wrappers.

State/persistence behavior: declared functions cover filesystem mutations, subprocess side effects, temporary files, stream global settings, and memory clearing.

Dependencies/integration: included broadly across the C++ codebase. Platform-specific behavior is supplied by `util-unix.cpp` or `util-win32.cpp` through `util.cpp`.

Risks/test signals: this is a high-fanout header, so API changes ripple widely. Test signals include platform parity for filesystem/process helpers and correct error messages from `System_error::message`.
