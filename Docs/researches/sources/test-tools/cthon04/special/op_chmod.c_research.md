# sources/test-tools/cthon04/special/op_chmod.c

## Purpose
checks that an already-open read/write file remains usable after its pathname is chmoded to no access.

## Important APIs, Types, and Functions
`main()`, helper `xxit()`, buffers `wbuf`/`rbuf`, `CHMOD_NONE`, `CHMOD_RW`, `tempnam()`, `chmod()`, `write()`, `read()`, and `system("ls")` are key.

## Control Flow and State
It creates a temp file, lists it, chmods it to no access, writes and rereads a fixed message through the open descriptor, compares data, restores permissions on DOS, unlinks, closes, and reports success.

## Persistence and Dependencies
state is a temp `nfs*` file and mode bits; cleanup differs on DOS/Unix. Dependencies: POSIX permission semantics, inherited open descriptors, `../tests.h` chmod masks.

## Integration Points, Risks, and Test Signals
Integration is open-file-after-permission-change validation. Risks include `tempnam()`, shelling out to `ls`, DOS-specific behavior, and no descriptor close before some failures. Signal is data compare ok and successful cleanup.
