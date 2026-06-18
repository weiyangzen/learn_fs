# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/share/compat.h

## Role

`share/compat.h` centralizes portability macros and wrappers needed to build FLAC across Unix, Windows, MSVC, MinGW, Android, and other C environments.

## Major Contents

- Defines `FLAC__off_t` and maps `fseeko`/`ftello` to 64-bit Windows equivalents where needed.
- Provides C99/inttypes compatibility for MSVC versions.
- Defines `flac_restrict`, `FLAC__U64L()`, and case-insensitive string comparison macros.
- Maps file and console functions to UTF-8 Windows wrappers on `_WIN32`, otherwise standard C/POSIX functions.
- Defines `flac_stat_s`, `flac_fstat`, math constants `M_LN2` and `M_PI` if absent.
- Declares `flac_snprintf()` and `flac_vsnprintf()` wrappers.

## Important Implementation Details

Windows paths use `share/win_utf8_io.h` to ensure `char *` filenames are treated as UTF-8. POSIX `flac_utime` maps to `utimensat()` when `_POSIX_C_SOURCE >= 200809L`, otherwise `utime()`.

There is a specific MSVC Windows XP toolset warning and workaround note around broken `_wstat64`/`_fstat64` behavior in some `/MT` builds.

## Risks / Edge Cases

- Feature behavior depends on build macros such as `HAVE_FSEEKO`, `_POSIX_C_SOURCE`, `_WIN32`, and compiler version.
- The `flac_utime` macro has different call expectations between `utimensat` and `utime` branches.
- Platform wrapper changes can affect metadata iterator file preservation and command-line tools.

## Dependencies

Includes standard headers conditionally and `share/win_utf8_io.h` on Windows.
