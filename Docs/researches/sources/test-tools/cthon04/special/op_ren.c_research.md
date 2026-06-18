# sources/test-tools/cthon04/special/op_ren.c

## Purpose
verifies writes through an open descriptor still work after another file is renamed over the open file name, covering NFS silly-rename style behavior.

## Important APIs, Types, and Functions
`main()`, `xxit()`, temp names `nfsa*`/`nfsb*`, `rename()`, `write()`, `read()`, `unlink()`, and close checks are key.

## Control Flow and State
It creates source A and open target B, renames A over B while B remains open, writes to B descriptor, rewinds, verifies data, unlinks the visible name, closes, verifies a second close fails, and exits with accumulated errors.

## Persistence and Dependencies
state is two temp names and the open file handle; failures may leave temp files. Dependencies: Unix rename/open descriptor semantics, `tempnam`, POSIX I/O, and SunOS/DOS skip conditionals.

## Integration Points, Risks, and Test Signals
Integration is open-renamed-file special testing. Risks are Unix-only semantics, command injection via temp names in `system("ls")`, and relying on old NFS behavior. Signals are rename success, data compare ok, and second close error.
