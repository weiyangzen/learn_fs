# File Research: sources/local-fs/dosfstools/src/common.c

Shared utilities and process-global mode state.

Globals:
- `interactive`
- `write_immed`
- `atari_format`
- `program_name`

Main functions:
- `die()` and `pdie()` print diagnostics and terminate.
- `alloc()` wraps `malloc()` and exits on failure.
- `qalloc()` and `qfree()` implement a simple linked allocation queue used for per-pass allocations such as `DOS_FILE` and LFN strings.
- `min()` returns the smaller integer.
- `xasprintf()` wraps `vasprintf()` and exits on failure; includes fallback `vasprintf()` when unavailable.
- `get_choice()` drives interactive/noninteractive repair choices. In noninteractive mode it prints a message and returns the provided default result.
- `get_line()` prompts and reads a line, temporarily restoring canonical terminal input and echo.
- `check_atari()` enables Atari FAT variant by inspecting `/proc/hardware` on configured m68k Linux builds.
- `generate_volume_id()` creates deterministic IDs from `SOURCE_DATE_EPOCH`, otherwise time/usec-based IDs, with random fallback.
- `validate_volume_label()` checks FAT volume-label constraints after DOS-codepage conversion.

Research notes:
- `get_choice()` includes a nested quit confirmation path for interactive fsck.
- `SOURCE_DATE_EPOCH` support makes labels/serials reproducible.
- Label validation returns a bitmask, allowing callers to distinguish lowercase warnings from hard invalidity.
