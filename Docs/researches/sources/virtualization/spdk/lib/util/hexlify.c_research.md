# File Research: sources/virtualization/spdk/lib/util/hexlify.c

This file converts binary data to lowercase hexadecimal strings and back.

`spdk_hexlify()` allocates a `len * 2 + 1` output string, converts each input byte through a nibble-to-character helper, and null-terminates the result. The generated alphabet is lowercase `0123456789abcdef`.

`spdk_unhexlify()` requires an even-length hex string, allocates `len / 2` bytes, accepts uppercase and lowercase hex digits, and returns null on odd length, invalid character, or allocation failure. Invalid input is logged.

The unhexlify result is raw binary and is not null-terminated beyond its allocated byte count; callers need to know the expected decoded length from the input string length.
