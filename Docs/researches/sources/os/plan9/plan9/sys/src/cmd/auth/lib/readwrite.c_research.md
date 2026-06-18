# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/lib/readwrite.c

Provides file-backed key and secret helpers. `findkey` and `setkey` read/write `DESKEYLEN` bytes at `<db>/<user>/key`; `findsecret` and `setsecret` read/write string secrets at `<db>/<user>/secret`.

`readfile` and `writefile` wrap simple open/read/write/close behavior with minimal error propagation.
