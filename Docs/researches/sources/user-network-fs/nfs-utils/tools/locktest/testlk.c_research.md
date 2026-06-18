# sources/user-network-fs/nfs-utils/tools/locktest/testlk.c

Purpose: `testlk.c` is a small manual tool for setting or querying POSIX byte-range locks on a file.

Important APIs and control flow: `main` parses `-r`, `-w`, `-b`, and `-t` to select read lock, write lock, blocking write lock, or `F_GETLK`; opens the target file read/write; fills `struct flock`; calls `fcntl`; prints success or conflicting lock details; and pauses after setting a lock so the lock remains held.

State, dependencies, and integration: Runtime state is the open file descriptor and kernel lock held by the process. It depends on `fcntl` locking and getopt.

Risks and test signals: The usage string omits option descriptions, `atoi` silently accepts bad ranges, and the process pauses indefinitely after lock acquisition. Tests should cover read/write/blocking/query modes, conflict reporting, invalid files, and signal cleanup.
