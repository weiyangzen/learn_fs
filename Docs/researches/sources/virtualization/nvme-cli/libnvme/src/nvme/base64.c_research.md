# File Research: sources/virtualization/nvme-cli/libnvme/src/nvme/base64.c

Small RFC4648-style Base64 encoder/decoder used by NVMe TLS key import/export.

Functions:
- `base64_encode(src, srclen, dst)`: emits Base64 characters and `=` padding, returns encoded byte count, and does not NUL-terminate.
- `base64_decode(src, srclen, dst)`: decodes Base64 input, returns decoded byte count, `-EINVAL` for invalid characters, and `-EAGAIN` for trailing non-zero leftover bits.

Dependencies:
- Uses `strchr` against a static Base64 alphabet.
- Error codes come from `<errno.h>`.

Important behavior:
- Caller must provide sufficiently large output buffers.
- Decoder accepts `=` padding by shifting zero bits into the accumulator.
- Embedded NUL in input is rejected because `!src[i]` triggers `-EINVAL`.

Risks and tests:
- No output capacity argument exists; all safety depends on callers sizing buffers correctly.
- Header comment says the alphabet is `[A-Za-z0-9+,]`, but the implementation uses standard `+/`.
- Test vectors should include empty input, 1/2/3-byte inputs, padding, invalid characters, embedded NUL, and malformed leftover bits.
