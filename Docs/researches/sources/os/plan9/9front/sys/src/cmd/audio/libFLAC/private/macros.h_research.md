# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/private/macros.h

## Role

`private/macros.h` provides internal `flac_min` and `flac_max` macros with safer single-evaluation variants where compiler support exists.

## Implementation Details

For GCC 4.3 and newer, it uses statement expressions and `__typeof__` to evaluate each argument once. `flac_min` uses `__COUNTER__` and token pasting to avoid local-name collisions. Other branches use `MIN`/`MAX` from `sys/param.h`, MSVC `__min`/`__max`, or fallback ternary macros.

## Risks / Edge Cases

- GCC statement expressions are non-standard C; fallback macros may evaluate arguments multiple times.
- Header behavior depends on platform headers defining `MIN` and `MAX`.
- The fallback ternary macros are less safe for expressions with side effects.

## Dependencies

May include `sys/param.h` or `stdlib.h` depending on platform macros.
