# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmp/strtomp.c

Implements `strtomp(char *a, char **pp, int base, mpint *b)`, parsing ASCII strings into `mpint` values for bases 10, 16, 32, and 64. It includes `os.h`, `<mp.h>`, `<libsec.h>`, and `dat.h`.

A static table initializer builds lookup arrays for base64, base32, hex, and decimal. Hex parsing packs nibbles directly into little-endian limbs. Decimal parsing consumes up to 9 digits at a time in native arithmetic, multiplying the accumulated `mpint` by powers of 10 and adding each chunk. Base64 and base32 scan valid alphabet spans, decode with `dec64`/`dec32`, and import the result with `betomp`.

`strtomp` skips spaces/tabs, accepts repeated `-` signs by multiplying sign by `-1`, defaults unsupported bases to base 16, normalizes the result, sets the sign, and optionally returns the parse end pointer. If no digits are parsed, it returns `nil`.

Notable detail: `from32` scans using `tab.t64` rather than `tab.t32` before calling `dec32`; as read, that widens the accepted scan set and may stop incorrectly for base32-only validation.
