# File Research: sources/os/plan9/plan9/sys/src/cmd/sha1sum.c

SHA digest command.

Key behavior:
- Computes SHA1 by default.
- `-2 bits` switches to SHA2-224, SHA2-256, SHA2-384, or SHA2-512.
- Reads stdin when no files are supplied; otherwise hashes each named file.
- Prints hex digest alone for stdin or digest plus filename for files.

Important details:
- Installs custom `%M` formatter for digest bytes.
- Uses libsec digest functions incrementally over 8192-byte reads.
- Continues past files that fail to open or read.

Filesystem relevance:
- Direct read-only file hashing utility.
