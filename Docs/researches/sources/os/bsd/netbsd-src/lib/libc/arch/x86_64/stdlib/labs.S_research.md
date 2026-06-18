# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/x86_64/stdlib/labs.S

## Summary
Implements x86_64 `labs()` and `llabs()` family aliases.

## Key Details
- Provides weak aliases for `imaxabs`, `llabs`, and `labs`.
- Tests 64-bit input sign and negates if negative.
- Returns absolute value in `%rax`.

## Notes
On NetBSD x86_64, `long`, `long long`, and `intmax_t` share this implementation.
