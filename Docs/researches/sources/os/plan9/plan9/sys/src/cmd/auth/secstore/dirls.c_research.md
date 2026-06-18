# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/secstore/dirls.c

Builds secstore directory listings. It reads a directory, sorts entries by name, and formats each regular readable file with aligned name, size, mtime, and base64 SHA1 digest.

`sha1file` streams file contents to compute digests. `dirls` returns a heap-allocated listing string consumed by `secstored` for `GET .`.
