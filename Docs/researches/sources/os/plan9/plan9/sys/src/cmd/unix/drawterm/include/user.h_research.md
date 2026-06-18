# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/include/user.h

User-space syscall and runtime API declarations for drawterm’s Plan 9 facade.

Key contents:
- Maps Plan 9 syscall names to `sys*` implementations and `sleep` to `osmsleep`.
- Declares file, directory, mount, pipe, read/write, stat, error string, network dial/listen, SSL, iounit, pread/pwrite, rendezvous, kproc, process, panic, sleep/yield, locking, time, and print functions.
- Declares `argv0` and local file-descriptor helper `lfdfd`.

Role in this group:
- Provides user-level call surface used by drawterm code while avoiding direct host libc usage.

Notable risks:
- Macro syscall remapping can make debugging symbol names non-obvious.
