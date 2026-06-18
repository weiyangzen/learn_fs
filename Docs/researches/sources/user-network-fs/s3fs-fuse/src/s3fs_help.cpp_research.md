# sources/user-network-fs/s3fs-fuse/src/s3fs_help.cpp

Purpose: provides static user-facing usage, full help, version, and short-version output for the `s3fs` command.

Important APIs and functions: `show_usage()` prints the short command form using `program_name`. `show_help()` prints usage and the large `help_string`. `show_version()` prints version, commit hash, crypto backend, license, and warranty text. `short_version()` returns a static compact version string.

Control flow: CLI option parsing calls these functions for `--help`, `--version`, argument errors, and launch logging. The help text documents mount, unmount, utility mode, s3fs options, FUSE/mount options, and misc flags.

State and persistence: no mutable local state; output is generated from static text plus compile-time `VERSION`/`COMMIT_HASH_VAL`, runtime `program_name`, and `s3fs_crypt_lib_name()`.

Dependencies and integration points: depends on `common.h` for `program_name` and version macros, and `s3fs_auth.h` for crypto library naming. It must track behavior implemented across option parsing, credential, cache, curl, and request modules.

Risks: static help can drift from actual option semantics. Because the help text mentions security behavior for TLS and credential logging, stale text can cause operational risk. Very large string literals are easy to edit incorrectly, including missing newline boundaries between adjacent entries.

Test signals: snapshot tests for `--help`, `--version`, and invalid bucket usage; checks that each documented credential option is accepted by parser; checks for security-warning text around insecure TLS/logging options.
