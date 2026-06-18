# File Research: sources/virtualization/nvme-cli/libnvme/src/nvme/base64.h

Tiny internal declaration header for Base64 helpers.

Exports:
- `int base64_encode(const unsigned char *src, int len, char *dst);`
- `int base64_decode(const char *src, int len, unsigned char *dst);`

Integration:
- Used by `crypto.c` for PSK digest and TLS key interchange encoding.
- No public libnvme visibility macro is applied, so this is an internal utility API.

Contract:
- Buffer sizing and NUL termination are caller responsibilities.
- Return values are byte counts or negative errno-style errors for decode.
