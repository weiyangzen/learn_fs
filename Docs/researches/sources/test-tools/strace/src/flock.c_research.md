# sources/test-tools/strace/src/flock.c

Decoder for BSD `flock`. It prints fd and lock operation flags from `flockcmds`, returning decoded. There is no persistent state. Dependencies are `<sys/file.h>`, `flockcmds`, and fd formatting. Risks are new lock operation bits or confusion between `flock` and fcntl record-lock structures. Tests should cover shared, exclusive, nonblocking, unlock, invalid combinations, and failed fd cases.
