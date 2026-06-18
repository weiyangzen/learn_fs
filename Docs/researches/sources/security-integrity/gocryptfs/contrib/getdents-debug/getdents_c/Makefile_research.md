# sources/security-integrity/gocryptfs/contrib/getdents-debug/getdents_c/Makefile

Purpose: This tiny Makefile builds the C `getdents` diagnostic binary.

Important APIs and targets: The `getdents_c` target compiles `getdents.c` with `gcc`.

Control flow and state: It creates one local executable as build state.

Dependencies and integration points: Complements the Go getdents diagnostic with a direct C syscall implementation.

Risks and test signals: Requires `gcc` and Linux syscall headers. Signal is successful compilation and executable behavior against test directories.
