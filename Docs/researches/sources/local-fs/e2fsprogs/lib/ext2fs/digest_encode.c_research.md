# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/digest_encode.c

Implements filename-safe digest encoding and decoding using a custom 64-character alphabet: uppercase letters, lowercase letters, digits, plus, and comma.

APIs:
- `ext2fs_digest_encode(const char *src, int len, char *dst)`
- `ext2fs_digest_decode(const char *src, int len, char *dst)`

Encoding packs input bytes into a little-endian bit accumulator and emits 6-bit symbols. Decoding reverses that process by finding each source character in the lookup table and emitting bytes whenever at least 8 bits are available.

Behavior:
- Encoded output is roughly 4/3 the input length.
- Decode returns `-1` for invalid characters or leftover nonzero accumulator bits.
- Functions return the number of bytes written and do not append a NUL terminator themselves.

Unit-test code under `UNITTEST` includes known digest vectors and command-line encode/decode helpers.

Implementation notes:
- The comment says `[a-zA-Z0-9_+]`, but the actual alphabet uses `+,` and no underscore.
- Decode uses `strchr`, making it simple but not constant-time.
