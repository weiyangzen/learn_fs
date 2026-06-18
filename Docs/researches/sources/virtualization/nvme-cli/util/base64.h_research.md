# File Research: sources/virtualization/nvme-cli/util/base64.h

Header for base64 helpers.

Exports:
- `base64_encode(const unsigned char *src, int len, char *dst)`
- `base64_decode(const char *src, int len, unsigned char *dst)`

Role:
- Public declaration layer for `util/base64.c`.
