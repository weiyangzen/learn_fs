# File Research: sources/local-fs/jfsutils/libfs/unicode_to_utf8.c

This file implements UTF-8 and 16-bit Unicode conversion helpers derived from old Linux `fs/nls.c`.

Main functions:
- `Unicode_Character_to_UTF8_Character()` encodes one `uint16_t` code unit into UTF-8 using a table that supports up to 6-byte historical UTF-8 forms.
- `Unicode_String_to_UTF8_String()` encodes a NUL-terminated `uint16_t` string into a UTF-8 byte buffer up to `maxlen`, skipping characters that cannot fit.
- `UTF8_Character_To_Unicode_Character()` decodes one UTF-8 sequence into one `uint16_t`, rejecting invalid continuation bytes and overlong forms.
- `UTF8_String_To_Unicode_String()` decodes a NUL-terminated UTF-8 byte string into a `uint16_t` buffer.

Integration points:
- Declared in `unicode_to_utf8.h`.
- Uses jfsutils integer typedefs from `jfs_types.h`.

Risks and notes:
- The implementation is old UTF-8 and permits 4- to 6-byte sequences even though the output is only `uint16_t`; values above `0xffff` truncate when stored.
- `UTF8_String_To_Unicode_String()` advances `op += size` after decoding one Unicode character, where `size` is bytes consumed, not UTF-16 code units produced. Multi-byte input therefore leaves gaps in the output count/buffer.
- The string conversion routines do not append a terminating NUL to the destination.
- There is no separate output-buffer length for UTF-8 to Unicode conversion.
