# sources/security-integrity/gocryptfs/contrib/getdents-debug/getdents_c/getdents.c

Purpose: This C diagnostic directly invokes the Linux `getdents` syscall to inspect directory entry bytes and errors.

Important APIs and functions: `main` opens a directory, calls `syscall(SYS_getdents, ...)` with a raw buffer, prints results, closes the descriptor, and repeats or exits depending on errors.

Control flow and state: Runtime state is a file descriptor, buffer, byte counters, and errno. It reads directory metadata but does not write files.

Dependencies and integration points: Used alongside the Go version to separate gocryptfs/FUSE issues from Go runtime or x/sys wrapper behavior.

Risks and test signals: Linux-specific syscall layout and buffer parsing can vary. Signals include reproducible byte counts and errno values compared with the Go diagnostic.
