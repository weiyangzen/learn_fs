# File Research: sources/os/bsd/freebsd-src/sys/kern/subr_scanf.c

## Purpose

`subr_scanf.c` provides kernel `sscanf()` and `vsscanf()` support derived from BSD `vfscanf`. It parses a NUL-terminated input string according to a subset of scanf-style conversions and writes converted values through a `va_list`.

## Supported Conversions

The implementation supports:

- Literal characters and `%%`.
- Assignment suppression with `*`.
- Width fields.
- Length modifiers: `h`, `hh`, `l`, `ll` via `QUAD`, `q`, `j`, `t`, `z`.
- Integers: `%d`, `%i`, `%o`, `%u`, `%x`, `%p`.
- Strings and characters: `%s`, `%c`, `%[...]`.
- `%n` to store the number of consumed input characters.

Floating-point flags are defined but no floating conversions are implemented in this file.

## Parser Structure

`sscanf()` is a thin wrapper around `vsscanf()`.

`vsscanf(inp, fmt0, ap)` tracks:

- `inr`: remaining input bytes, initialized with `strlen(inp)`.
- `nread`: total consumed characters.
- `nassigned`: number of assigned fields.
- `nconversions`: conversions attempted.
- `width`, `flags`, `base`, and conversion type.
- `buf[32]` for numeric tokens.
- `ccltab[256]` for scansets.

Whitespace in the format consumes any amount of input whitespace. Non-`%` format characters must match literally. For most conversions, leading input whitespace is skipped unless `NOSKIP` is set.

## Integer Conversion

Integer parsing accumulates a bounded token into `buf`, then calls either `strtoq` or `strtouq`. It handles:

- Optional sign.
- `%i` base detection.
- Octal/decimal/hex bases.
- Optional `0x` prefix for `%x`, `%i`, and `%p`.
- Pushback of a lone sign or trailing `x` from `0x`.

Assignment writes to the destination type selected by length flags. `%p` writes through `void **` after converting the integer to `uintptr_t`.

## String, Character, And Scanset Conversion

`%c` copies exactly `width` characters, defaulting to 1, and does not skip whitespace.

`%s` copies non-whitespace characters and NUL-terminates when not suppressed. The implementation permits zero-length string assignment after leading whitespace handling.

`%[...]` uses `__sccl()` to build an inclusion table. It requires at least one matching character unless input failure occurs. Negated scansets with `^`, leading `]`/`-`, ranges such as `a-z`, and historical range behavior are handled.

## Return Semantics

On input failure before any conversion, `vsscanf()` returns `-1`. On later input failure, it returns the number of assigned fields. On match failure, it returns the number of assigned fields.

`%n` counts as a conversion but not an assignment in the `nassigned` return value.

## Dependencies

The file depends on kernel `ctype`, string conversion routines, `stdarg`, and basic system headers.

## Maintenance Notes

The numeric buffer is fixed at 32 bytes, so very long numeric fields are intentionally truncated by width handling. This is traditional scanf behavior for the local implementation, but future extension should preserve bounded token accumulation.

The scanset parser uses a 256-byte table indexed by unsigned input characters. Any change to character signedness paths should keep the explicit casts around table lookup.
