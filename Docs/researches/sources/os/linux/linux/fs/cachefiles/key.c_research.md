# File Research: sources/os/linux/linux/fs/cachefiles/key.c

## Purpose
Encodes FS-Cache binary cookie keys into filesystem-safe CacheFiles object names.

## Main Elements
- `cachefiles_charmap`: 64-character alphabet for custom base64-like encoding.
- `cachefiles_filecharmap`: marks directly usable printable filename characters, excluding control characters, spaces, tabs, and `/`.
- `how_many_hex_digits()`: helper for compact integer encoding size estimates.
- `cachefiles_cook_key()`: chooses direct string encoding, 32-bit comma-separated hex encoding in the smaller endian representation, or base64-like encoding; stores the resulting name in `object->d_name`.

## Dependencies And Integration
Called during object lookup before traversing the backing cache directory. Uses FS-Cache cookie keys and Linux `NAME_MAX` constraints.

## Risk Notes
The code assumes keys fit within `NAME_MAX - 3` and that binary keys considered for 32-bit hex encoding are padded to a full word count. Filename safety is critical because names are passed directly into VFS lookup/create helpers.
