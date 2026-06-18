# sources/test-tools/lcov/scripts/get_signature

Purpose: standalone sample version-script that uses an md5 checksum as the file version identifier and compares versions by exact string equality.

Important APIs: command modes are `get_signature [--allow-missing] filename` and `get_signature --compare old_version new_version filename`. It prints the checksum or an empty line for allowed missing files, and exits nonzero when comparison strings differ.

Control flow and state: argument parsing validates mode arity. In compare mode no filesystem access is needed. In extraction mode the script checks existence, canonicalizes the path with `abs_path`, runs `md5sum`, captures the first token, prints it, and exits with the `md5sum` status.

Dependencies and integration: depends on `Getopt::Long`, `Cwd`, POSIX import that is unused, and the external `md5sum` program. It is a process-based callback compatible with lcov `--version-script`.

Risks and test signals: command substitution does not quote the path, so filenames containing shell metacharacters or spaces are unsafe. `md5sum` is not portable to all platforms. Tests should include compare mode, missing-file behavior, and checksum matching on simple files; security-sensitive callers should prefer a Perl digest library.
