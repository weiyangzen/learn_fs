# sources/storage-engines/wiredtiger/test/suite/test_bug018.py

Purpose: regression for WT-3590, where a write failure during connection close could leave tables updated in one transaction out of sync after recovery.

Important APIs/types/functions: `suite_subprocess`, `copy_wiredtiger_home`, Linux `/proc/self/fd` inspection, `wiredtiger.WiredTigerError`, `expectedStderrPattern`, `run_subprocess_function`, and cursor iteration. The class enables logging and is skipped for nonstandalone and tiered hooks.

Control flow: in a subprocess, open filler file descriptors, create two file tables, commit the same key/value to both in one transaction, close filler descriptors, close the OS file descriptor for the second table underneath WiredTiger, then close the connection expecting a possible error. The parent copies the home for forensics, reopens, reads table 1, tries to read table 2, and asserts both result sets are equal, treating inability to open table 2 as an empty result only if error output exists.

State/persistence behavior: tests atomic recovery of a transaction spanning multiple files when one file write fails late. Logging and recovery must leave both tables aligned.

Dependencies/integration: Linux-specific file descriptor manipulation, subprocess isolation, recovery, error capture, and filesystem copy helpers.

Risks/test signals: platform and sanitizer sensitive; skipped outside Linux/POSIX and for TSan. Failure is divergence between tables or unhandled close/recovery errors.
