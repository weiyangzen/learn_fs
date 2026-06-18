# sources/security-integrity/gocryptfs/contrib/getdents-debug/readdirnames/readdirnames.go

Purpose: This diagnostic uses higher-level Go directory APIs to repeatedly read entry names from a directory.

Important APIs and functions: It opens a path, calls `Readdirnames` or equivalent, prints names/errors, closes, and repeats after a short sleep.

Control flow and state: It observes directory listing behavior without mutating files. Runtime state is the open directory and returned name slice.

Dependencies and integration points: Complements raw getdents tools by showing behavior through Go's `os.File` directory abstraction over gocryptfs/FUSE mounts.

Risks and test signals: Output depends on directory contents and Go runtime directory buffering. Signals are consistent names and error behavior compared with raw syscall diagnostics.
