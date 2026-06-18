# File Research: sources/os/bsd/netbsd-src/lib/libc/hash/hmac.c

Implements generic `hmac(name, key, klen, text, tlen, digest, dlen)` dispatching by algorithm name.

Supported algorithms:
`md2`, `md4`, `md5`, `rmd160`, `sha1`, `sha224`, `sha256`, `sha384`, `sha512`.

Behavior:
- Looks up algorithm metadata: context size, digest size, block size, init/update/final callbacks.
- If the key is longer than the hash block size, hashes it first.
- Builds HMAC ipad/opad buffers of fixed `HMAC_SIZE` 128 bytes.
- Computes inner hash over `ipad || text`, then outer hash over `opad || inner_digest`.
- Returns full digest size, or `-1` for unknown algorithm.

Notable implementation risk: the short-output path uses a temporary buffer when `dlen < digsize`, but the outer update reads from `digest` rather than the temporary inner digest buffer, which is suspicious for truncated output callers.
