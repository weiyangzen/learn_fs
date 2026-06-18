# sources/security-integrity/gocryptfs/contrib/getdents-debug/getdents/getdents.go

Purpose: This Go diagnostic repeatedly calls the Linux `getdents` syscall on a directory to debug directory entry behavior.

Important APIs and functions: It opens a directory with `unix.Open`, allocates a buffer, calls `unix.Getdents`, prints byte counts and errors, closes the descriptor, and sleeps between iterations.

Control flow and state: The command loops indefinitely or until error/interrupt, repeatedly observing directory stream state. It does not persist repository state.

Dependencies and integration points: Used to debug gocryptfs/FUSE directory listing behavior, especially low-level `getdents` quirks.

Risks and test signals: Linux-specific and diagnostic only. Signals are consistent total bytes read and surfaced syscall errors while directory contents change or remain stable.
