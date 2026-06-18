# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/share/safe_str.h

## Role

`share/safe_str.h` provides small bounded string helpers that guarantee NUL termination for copy and concatenation operations.

## API Surface

- `safe_strncat(dest, src, dest_size)` appends with `strncat()` using the available destination size and then forces the final byte to NUL.
- `safe_strncpy(dest, src, dest_size)` copies up to `dest_size - 1` bytes and forces the final byte to NUL.

## Important Implementation Details

Both functions no-op for `dest_size < 1` and return `dest`. The comments state that truncation is allowed when the destination is too short.

## Risks / Edge Cases

- `safe_strncat()` calls `strlen(dest)` and assumes `dest` is already NUL-terminated within `dest_size`.
- The header uses `strncat`, `strlen`, and `strncpy` but does not include `<string.h>` itself, so callers must include it first.
- These helpers do not report truncation.

## Dependencies

Relies on C string library declarations supplied by including translation units.
