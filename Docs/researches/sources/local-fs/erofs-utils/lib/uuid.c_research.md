# File Research: sources/local-fs/erofs-utils/lib/uuid.c

## Scope

This file provides UUID generation and parsing for erofs-utils, using libuuid when available and local fallback logic otherwise.

## Public And Internal APIs Covered

- `erofs_uuid_generate()` fills a 16-byte UUID buffer.
- `erofs_uuid_parse()` parses canonical hyphenated UUID strings into 16 bytes.
- Fallback-only `s_getrandom()` wraps `getrandom()` or the Linux syscall and optionally falls back to `rand()` for insecure generation when the syscall is unavailable.

## Control Flow And Behavior

- With libuuid, generation loops until `uuid_generate()` returns a non-null UUID and parsing delegates to `uuid_parse()`.
- Without libuuid, generation requests random bytes with insecure mode enabled, asserts success, and sets version/variant bits before copying to the caller buffer.
- `s_getrandom()` retries interrupted calls, detects unsupported `GRND_INSECURE` through `EINVAL` and disables the flag for retry, and falls back to `rand()` only for insecure generation when `getrandom` is unavailable.
- Fallback parsing reads exactly 16 two-hex-digit bytes and requires hyphens after the conventional 4th, 6th, 8th, and 10th bytes, with no trailing characters.

## State And Data Structures

- Maintains process-global `erofs_grnd_flag`, initialized to `GRND_INSECURE` or its numeric value, and downgraded to zero if the kernel rejects it.

## Dependencies

- Optional libuuid; otherwise libc, `getrandom()` or Linux `syscall(__NR_getrandom)`, and EROFS definitions/macros.

## Risks And Invariants

- Fallback generation depends on `BUG_ON(res != 0)`, so entropy/syscall failure is fatal outside the explicit insecure fallback path.
- The fallback version/variant bit placement uses local byte indexing; compatibility depends on matching the project’s UUID byte-order conventions.
- Parser rejects malformed hex/hyphen layout strictly and returns `-EINVAL` for local fallback failures.
