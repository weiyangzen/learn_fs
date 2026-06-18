# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/u9fs/readn.c

- Role: Blocking helper to read up to an exact byte count unless EOF/error occurs.
- Key function: `readn(f, av, n)` loops until `n` bytes are read, returns the first error/EOF if no bytes were read, or partial count otherwise.
- Integration: Used for 9P message framing and random seed reads.
- Risks/notes: Does not retry on `EINTR`; callers treat short reads as fatal in protocol paths.
