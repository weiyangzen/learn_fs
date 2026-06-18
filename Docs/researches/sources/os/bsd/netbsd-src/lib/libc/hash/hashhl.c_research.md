# File Research: sources/os/bsd/netbsd-src/lib/libc/hash/hashhl.c

Generic high-level digest helper template, compiled by defining `HASH_ALGORITHM` and `HASH_INCLUDE`.

Generated APIs include:
- `<ALG>End`
- `<ALG>FileChunk`
- `<ALG>File`
- `<ALG>Data`

Behavior:
- `End` finalizes binary digest and hex-encodes it, allocating output if `buf == NULL`.
- `FileChunk` opens a file with `O_CLOEXEC`, optionally seeks, reads chunks, and updates the hash context.
- `File` hashes the whole file.
- `Data` hashes an in-memory buffer.

It uses macro name construction for algorithm-specific context, length, and function prefixes, plus weak aliases outside tool builds.
