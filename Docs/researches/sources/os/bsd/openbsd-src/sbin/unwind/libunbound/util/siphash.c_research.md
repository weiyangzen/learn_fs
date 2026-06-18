# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/siphash.c

Contains the SipHash reference implementation, lightly adapted for Unbound.

Core behavior:
- Implements default SipHash-2-4 with `cROUNDS = 2` and `dROUNDS = 4`.
- `siphash(in, inlen, k, out, outlen)` accepts a 16-byte key and writes either 8 or 16 output bytes.
- Input is processed in 8-byte little-endian words, with tail bytes packed into the final block.
- For 16-byte output, it applies the SipHash-128 domain-separation steps and emits a second 64-bit word.

Adaptations:
- Uses `config.h` rather than standalone standard includes.
- Includes `util/siphash.h` to avoid missing-prototype warnings.
- The assert on `outlen` is inside the function for C90 compatibility.
- Fallthrough annotations use `ATTR_FALLTHROUGH`.

Notes:
- This is a keyed hash, suitable for hash-table hardening and short authenticator-style uses, but the file exposes only the one-shot API.
- Debug tracing is compiled only with `DEBUG`.
