# sources/sync-backup/bup/lib/bup/bloom.py

## Purpose
Implements bup Bloom filter readers/writers over mmap-backed `.bloom` files, using C helpers for k=4/k=5 bit addressing. It accelerates object existence checks against pack indexes.

## Important APIs, Types, and Functions
Constants include `BLOOM_VERSION`, `MAX_BITS_EACH`, `MAX_BLOOM_BITS`, and `MAX_PFALSE_POSITIVE`. Classes are `_BloomBase`, `BloomReader`, `BloomWriter`, `BloomInvalid`, and `BloomNotFound`; helpers include `_validate_and_get_info`, `_create`, `_open_write_map`, and `clear_bloom`.

## Control Flow
Readers open and mmap existing bloom files, validate the `BLOM` header, version, bit count, k, entries, and idx names. Writers create or update through temporary files, choose k/bits from expected entries, add index shatables, optionally delay writes with a private mmap, update entry counts, append idx names, and atomically rename into place.

## State and Persistence Behavior
Persistent state is the `.bloom` file: 16-byte header, bit array of `2**bits` bytes, and NUL-delimited idx names. Runtime state tracks mmap/file/temp path, entries, k, bits, and delaywrite mode.

## Dependencies and Integration Points
Depends on `_helpers.bloom_contains`/`bloom_add`, bup mmap helpers, logging, umask handling, and index objects exposing `shatable`/`name`. Used by `bup bloom` and object index caches.

## Risks and Test Signals
Risks include false-positive tuning, invalid/old/new bloom rejection, interrupted temp files, mmap dirty-page behavior, and idx-name mismatch. Signals are header validation, pfalse calculations, object membership, atomic close/rename, and check-mode verification against idx contents.
