# sources/test-tools/fio/lib/strntol.c

Purpose: bounded-length wrapper around `strtol`.

Important APIs/functions: `strntol(const char *str, size_t sz, char **end, int base)`.

Control flow: skips leading spaces within the bounded region, rejects empty or too-large slices for its 24-byte stack buffer, copies exactly `sz` bytes to a NUL-terminated buffer, calls `strtol`, and maps the returned end pointer back into the original string.

State/persistence: no state. Returns 0 and sets `end` to original `str` on rejected sizes.

Dependencies/integration: used by pattern parsing when decimal text must stop before a later `0x` sequence or other bounded region.

Risks/test signals: the fixed buffer assumes LONG_MIN/MAX decimal representations fit under 24 bytes. Overflow is left as `strtol` result and errno behavior. Tests should cover leading spaces, partial strings, overflow, invalid input, and end-pointer mapping.
