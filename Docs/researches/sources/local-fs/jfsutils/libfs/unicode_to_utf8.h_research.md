# File Research: sources/local-fs/jfsutils/libfs/unicode_to_utf8.h

This header declares the four UTF-8/Unicode conversion helpers:

- `Unicode_Character_to_UTF8_Character()`
- `Unicode_String_to_UTF8_String()`
- `UTF8_String_To_Unicode_String()`
- `UTF8_Character_To_Unicode_Character()`

It includes `jfs_types.h` for `uint8_t` and `uint16_t` and uses guard `_UNICODE_TO_UTF8_H`.
