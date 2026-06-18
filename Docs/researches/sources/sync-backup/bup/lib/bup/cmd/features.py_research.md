# sources/sync-backup/bup/lib/bup/cmd/features.py

## Purpose
`features.py` reports build/runtime capabilities for the installed bup executable: version, source commit/date, Python version, readline support, POSIX ACL support, and xattr support.

## APIs and Control Flow
`show_support(out, bool_opt, what)` formats a yes/no capability line. `main(argv)` rejects arguments, creates a byte stdout stream, prints `version.version`, `version.commit`, `version.date`, `platform.python_version`, and probes `_helpers.readline`, `_helpers.read_acl`, and `metadata.xattr`.

## State, Dependencies, Integration, Risks, Tests
The command is read-only and persists nothing. It depends on optional compiled helper symbols, metadata feature flags, and the generated `bup.version` module. It integrates with support/debug workflows and remote `bup on` commands where `features` is allowed without local repository server setup. Risks are misleading reports if optional helper imports are stubbed or if platform encoding cannot ASCII-encode the Python version. Test signals are no-argument enforcement and capability output under helper builds with/without readline, ACL, and xattr symbols.
