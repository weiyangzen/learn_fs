# File Research: sources/local-fs/xfsprogs/db/obfuscate.c

## Purpose
Provides hash-preserving name obfuscation and alternate-name generation for directories and attributes.

## Main Interfaces
- `obfuscate_name(hash, name_len, name, is_dirent)` rewrites names of length at least five to another same-length name with the same XFS directory/attr hash.
- `find_alternate(name_len, name, seq)` flips paired bits to generate deterministic same-hash alternates when an obfuscated name collides.

## Control Flow
`obfuscate_name()` fills all but the last five bytes with random valid filename characters, computes the five trailing bytes needed to recover the requested hash, repairs invalid slash/NUL bytes by paired bit adjustments, and retries for ASCII case-insensitive directory hashes if necessary. `find_alternate()` interprets sequence bits as selected overlap-preserving bit flips and calls `flip_bit()` for each selected pair.

## Dependencies
Uses global mount feature checks for ASCII case-insensitive names and libxfs ASCII case transformation helpers.

## Risks And Invariants
- Names shorter than five bytes are not obfuscated by `obfuscate_name()`.
- Generated names must avoid `/` and NUL.
- ASCII case-insensitive filesystems require retrying correction bytes that would be transformed during hashing.
