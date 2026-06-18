# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/hmac.c

Implements RFC 2104-style HMAC wrappers for SHA1 and MD5. It includes `os.h` and `<libsec.h>`.

The static helper `hmac_x` accepts a digest function pointer, digest length, message chunk, key, output digest pointer, and optional digest state. It builds the inner pad on first call, streams data through the digest function, and on final call computes the outer digest over the outer pad plus inner digest.

Public wrappers are `hmac_sha1` and `hmac_md5`. The implementation rejects keys longer than 64 bytes instead of hashing them down, so callers must pre-process long HMAC keys if RFC-compatible long-key behavior is needed.
