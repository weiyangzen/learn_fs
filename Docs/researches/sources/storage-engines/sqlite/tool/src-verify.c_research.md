# sources/storage-engines/sqlite/tool/src-verify.c

## Purpose
`src-verify.c` verifies that a Fossil-generated SQLite source checkout matches its `manifest` and `manifest.uuid`. It recomputes the check-in SHA3-256 hash from the manifest, verifies every listed file against its SHA1 or SHA3 hash, and reports either an OK version or changed/missing files.

## Important APIs, types, and functions
The file is self-contained and implements SHA1 (`SHA1Context`, `SHA1Transform()`, `SHA1Init()`, `SHA1Update()`, `SHA1Final()`) and SHA3-256 (`SHA3Context`, `KeccakF1600Step()`, `SHA3Init()`, `SHA3Update()`, `SHA3Final()`). `DigestToBase16()` serializes digests. `sha1sum_file()` and `sha3sum_file()` hash disk files. `defossilize()` decodes Fossil filename escapes. `errorMsg()` and `errorMsgNH()` produce human and script-oriented error output.

## Control flow
`main()` handles debug hash modes (`--sha1`, `--sha3`) or normal verification. In normal mode it opens `<ROOT>/manifest`, hashes its pre-comment lines to derive `zVers`, then rewinds and processes `F` records. Each file path is appended to the root path, defossilized, checked for readability, and hashed according to the manifest hash length. It finally verifies `<ROOT>/manifest.uuid` is a 64-character SHA3 line equal to `zVers`.

## State and persistence behavior
No persistent state is modified. The program reads the manifest, manifest.uuid, and source files. Runtime state is bounded to fixed-size path/hash/line buffers plus hash contexts.

## Dependencies and integration points
The utility uses only the C standard library plus `access()` compatibility wrappers on Windows. It is meant to run in SQLite/Fossil release or source-integrity checks and can be compiled independently.

## Risks and edge cases
Path and line buffers are large but fixed; extremely long manifest records are truncated into `zFile`/`zHash` and treated as manifest errors or incorrect files. The code assumes the check-in hash is SHA3-256 and only accepts file hashes of length 40 or 64. Option parsing checks `argv[1]` for `--sha1`/`--sha3` inside the loop, so those modes are intended only as first-argument modes.

## Test signals
Signals include `src-verify ROOT` printing `OK <hash>`, `-x` first-line hash plus changed files, `-v` manifest debug listing, `--sha1 FILE...` and `--sha3 FILE...` outputs, deliberate modified/missing files, malformed manifest hashes, and mismatched `manifest.uuid`.
