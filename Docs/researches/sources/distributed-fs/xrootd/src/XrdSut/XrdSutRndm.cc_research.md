# sources/distributed-fs/xrootd/src/XrdSut/XrdSutRndm.cc

## Purpose

This file implements the XrdSut random helper used to generate random strings, byte buffers, random tags, and unsigned integers for security protocol support.

## Important APIs, types, and functions

`XrdSutRndm::Init` seeds the C library PRNG from `/dev/urandom` if possible or `time(0)` otherwise. `GetString(const char *,...)` maps option names to character classes. `GetString(int,...)` returns null-terminated random strings from printable, alphanumeric, hex, or crypt-like sets. `GetBuffer` returns caller-owned random bytes, optionally filtered by the same classes. `GetRndmTag` returns an eight-character crypt-like tag. `GetUInt` returns `rand()`.

## Control flow

All generation lazily initializes the static `fgInit` flag. String generation repeatedly pulls `rand()` values, slices bits into candidate characters, checks a static mask, and appends accepted characters until the requested length is reached. Buffer generation similarly emits four candidate bytes per `rand()` call and filters when requested.

## State and persistence behavior

The only state is the process-global `fgInit` flag and the C library PRNG state seeded by `srand`. No persistence occurs.

## Dependencies and integration points

The file depends on POSIX `open/read/close`, `time`, `rand/srand`, `XrdOucString`, and XrdSut tracing. It is used by XrdSut template resolution and by XrdCrypto/XrdSec password/GSI code for salts, tags, keys, IV-like buffers, and serial values.

## Risks and edge cases

This is not a cryptographically strong generator despite seeding from `/dev/urandom`; after seeding it uses `rand()`, which is predictable and global-state-based. It is not thread-safe around initialization or PRNG access. If `/dev/urandom` is unavailable, seeding with `time(0)` is weak. Negative lengths are not validated before `new char[len+1]` or `new char[len]`. Debug logging can print generated secret material. Character masks are hand-coded and should be tested carefully.

## Test signals

Tests should cover each character class, invalid option fallback, zero and negative length handling, forced reinitialization, `/dev/urandom` fallback behavior via dependency injection or platform tests, caller ownership of `GetBuffer`, and security review signals for consumers requiring cryptographic randomness.
