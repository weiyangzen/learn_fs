# sources/storage-engines/sqlite/tool/mksourceid.c

## Purpose

Standalone build utility that reads a Fossil manifest and emits SQLite's source id: check-in date plus SHA3-256 of the manifest content. It also verifies every `F` manifest entry against the corresponding working-tree file and marks the source id as modified when any file is missing or hash-mismatched.

## Important APIs, control flow, and dependencies

The file embeds SHA3/Keccak and SHA1 implementations. `SHA3Context`, `KeccakF1600Step()`, `SHA3Init()`, `SHA3Update()`, `SHA3Final()`, and `DigestToBase16()` implement SHA3 output; `SHA1Context`, `SHA1Transform()`, `SHA1Init()`, `SHA1Update()`, `SHA1Final()`, and `sha1sum_file()` support legacy 40-character Fossil hashes. `sha3sum_file()` hashes files for newer manifest entries. `nextToken()` destructively tokenizes manifest lines. `main()` parses `-v`, opens the manifest, excludes lines beginning `# Remove this line` from the manifest hash, extracts the date from `D` records, verifies each `F` file hash, and prints either `date hash` or `date hashalt1` when verification fails.

## State, persistence, and integration

No state is written. The tool reads the manifest and all referenced files by relative path from the current working directory, so it is tightly coupled to the Fossil checkout layout used by SQLite release builds. Endianness handling is embedded in both hash implementations to keep output stable across architectures. The emitted text feeds generated version/source-id constants elsewhere in the SQLite build.

## Risks and test signals

Important risks are manifest parser assumptions, path handling from the current directory, SHA3/SHA1 endianness bugs, and line-buffer truncation for unusual manifest entries. A missing or changed file deliberately changes the suffix rather than failing hard unless verbose diagnostics are requested. Test signals include comparing against Fossil's own manifest hash, running on clean and modified checkouts, verifying legacy SHA1 and SHA3 manifests, and cross-platform byte-for-byte source-id stability.
