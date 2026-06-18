# File Research: sources/os/linux/linux-stable/fs/cachefiles/key.c

This file converts FS-Cache binary cookie keys into safe backing filesystem filenames.

Key function:
- `cachefiles_cook_key()` takes the raw cookie key from `fscache_get_key()` and stores an allocated filename in `object->d_name`.

Encoding strategy:
- If the key consists entirely of filename-safe printable characters, it uses direct string encoding prefixed with `D`.
- Otherwise, it compares compactness of big-endian and little-endian 32-bit hex chunk encodings:
  - `S` indicates big-endian hex chunks.
  - `T` indicates little-endian hex chunks.
  - subsequent chunks are comma-separated.
- If hex is not smaller than custom base64, it uses base64-like encoding:
  - prefix `E`
  - second character records padding count
  - character map is digits, lowercase, uppercase, underscore, hyphen.

Constraints and assumptions:
- The key length must fit within `NAME_MAX - 3`.
- Hex encoding assumes the key has been padded to a whole number of 32-bit words.
- `/`, whitespace, control characters, space, and tab are excluded from direct filename rendering.

Purpose:
- Provides deterministic, path-safe, compact names for cache object files under fanout directories.
