# File Research: sources/os/bsd/netbsd-src/lib/libedit/parse.h

## Purpose
Private declarations for editrc command parsing and escape decoding.

## Main Declarations
- `parse_line`
- `parse__escape`
- `parse__string`
- `parse_cmd`

## Integration
`map_bind` uses `parse__string` and `parse_cmd` for user bindings. Configuration loading uses `parse_line`/`el_wparse`.

## Risks And Notes
This header exposes low-level parsing helpers used by multiple subsystems; behavior changes can affect both startup config parsing and interactive `bind` handling.
