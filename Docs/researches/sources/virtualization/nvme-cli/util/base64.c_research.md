# File Research: sources/virtualization/nvme-cli/util/base64.c

RFC4648-style base64 encode/decode implementation.

Key elements:
- Uses standard Base64 alphabet with `+` and `/`.
- `base64_encode` consumes bytes, emits 6-bit alphabet values, and pads with `=`.
- Encoded output is not NUL-terminated by the function.
- `base64_decode` maps characters through `strchr`, handles `=`, rejects invalid or NUL characters with `-EINVAL`, and rejects leftover nonzero bits with `-EAGAIN`.

Role:
- Small local utility for encoding/decoding binary data where nvme-cli needs textual representation.
