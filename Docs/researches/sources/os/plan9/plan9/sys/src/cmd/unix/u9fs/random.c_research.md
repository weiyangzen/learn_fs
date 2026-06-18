# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/u9fs/random.c

- Role: Supplies `randombytes` for authentication nonce/key material in u9fs.
- Key functions: `getseed` tries `/dev/urandom`, then falls back to time and PID; `randombytes` seeds libc `random()` once and fills output bytes.
- Integration: Declared in `u9fs.h`; consumed by auth modules.
- Risks/notes: After seeding, bytes come from `random()`, not directly from a cryptographic RNG; adequate only for legacy compatibility, not modern cryptographic use.
