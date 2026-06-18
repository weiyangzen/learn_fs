# File Research: sources/local-fs/udftools/libudffs/unicode.c

UDF compressed Unicode and d-string conversion routines.

Functions:
- `decode_utf8`: decodes UDF compressed Unicode with compression ID 8 or 16 into UTF-8, including UTF-16 surrogate handling.
- `encode_utf8`: encodes UTF-8 input into UDF compressed Unicode, choosing 8-bit compression when possible and 16-bit otherwise.
- `decode_locale`: decodes UDF compressed Unicode into the current locale via wide-character conversion.
- `encode_locale`: encodes current-locale strings into UDF compressed Unicode.
- `decode_string`: decodes ECMA d-strings using the encoding flags on `struct udf_disc`.
- `encode_string`: encodes into ECMA d-string format and stores the payload length in the final field byte.

Supported output/input modes are controlled by `FLAG_UTF8`, `FLAG_LOCALE`, `FLAG_UNICODE8`, and `FLAG_UNICODE16`.

Error behavior:
- Buffer-size and invalid-format cases generally return `(size_t)-1`.
- Some invalid locale/UTF-8 conversion cases print an error with `appname` and exit.

Key role: all label, identifier, and file-name encoding/decoding for UDF descriptors.
