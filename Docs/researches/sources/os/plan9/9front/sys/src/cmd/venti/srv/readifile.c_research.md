# File Research: sources/os/plan9/9front/sys/src/cmd/venti/srv/readifile.c

`readifile` is a tiny diagnostic wrapper around `readifile()`. It reads an index/config-style `IFile` from the named file and writes the underlying `ZBlock` bytes to stdout.

It does no parsing beyond the shared helper and exits fatally on read failure. Its main value is verifying or extracting how the Venti `IFile` abstraction sees a file.
