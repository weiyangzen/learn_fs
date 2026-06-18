# File Research: sources/local-fs/udftools/wrudf/ide-pc.c

## Role

Low-level ATAPI/MMC packet command wrapper for CD/DVD writer operations via Linux `CDROM_SEND_PACKET`.

## Main Responsibilities

- Provides a thin C function wrapper around many MMC commands.
- Maintains global last ioctl return value and request sense data for diagnostic reporting.
- Handles command descriptor block construction and endian conversion.
- Provides mode sense/select helpers for write parameters and capability pages.

## Important Functions

- `fail()` prints an error and exits.
- `get_sense_data()` and `get_sense_string()` expose the last request sense state.
- `initpc()` zeroes `cdrom_generic_command`, attaches global sense data, and sets defaults.
- Media/drive commands:
  - `blank()`
  - `close_track_session()`
  - `format()`
  - `set_cdspeed()`
  - `synchronize_cache()`
  - `test_unit_ready()`
  - `getDriveState()`
  - `mediumRemoval()`
  - `startStopUnit()`
- Query commands:
  - `inquiry()`
  - `read_reccapacity()`
  - `read_buffercapacity()`
  - `read_discinfo()`
  - `read_header()`
  - `read_trackinfo()`
  - optional `get_configuration()` under `MMC2`
- Data commands:
  - `readCD()`
  - `writeCD()`
  - optional `verify()` under `MMC2`
- Mode-page helpers:
  - `mode_sense()`
  - `mode_select()`
  - `get_writeparams()`
  - `set_writeparams()`
  - `get_capabilities()`

## Notable Behaviors

- Uses fixed 2048-byte sector sizing for `readCD()` and `writeCD()`.
- Converts selected returned structure fields from big-endian to CPU order after reads.
- Converts write parameters to big-endian before `mode_select()` and restores them afterward.
- `mode_sense()` first requests only the mode header to determine full allocation length, then allocates and reads the full page.
- `getDriveState()` retries `TEST UNIT READY` after sleeping and maps selected sense codes to operational/tray-open/no-disc states.

## Dependencies

- Linux `linux/cdrom.h` and `CDROM_SEND_PACKET`.
- `ide-pc.h` for MMC structures and constants.
- `bswap.h` for endian conversion.

## Research Notes

This is older, Linux-specific CD writer plumbing. It deliberately models MMC structures rather than relying only on Linux cdrom abstractions, which makes it useful for `wrudf` but tightly coupled to the kernel packet command ABI.
