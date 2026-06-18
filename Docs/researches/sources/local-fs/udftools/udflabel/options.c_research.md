# File Research: sources/local-fs/udftools/udflabel/options.c

## Role

Command-line parser and identifier encoder for `udflabel`.

## Supported Options

- Block/read hints: `--blocksize`, `--startblock`, `--lastblock`, `--vatblock`.
- Update controls: `--force`, `--no-write`.
- Identifiers: `--uuid`, `--lvid`, `--vid`, `--vsid`, `--fsid`, `--fullvsid`, `--owner`, `--organization`, `--contact`, `--appid`, `--impid`.
- Charset controls: `--locale`, `--u8`, `--u16`, `--utf8`.
- Positional `new-label`, treated as both `--lvid` and `--vid`.

## Important Functions

- `usage()` prints detailed help.
- `process_uuid_arg()` accepts explicit 16-byte lowercase hex UUID or `random`, which generates a time-prefixed random value.
- `process_vid_lvid_arg()` encodes LVID and/or VID, truncating VID from label input when necessary but rejecting explicit oversized `--vid`.
- `parse_args()` validates and encodes all options into caller-provided buffers with sentinel values.

## Validation Rules

- Block size must be a power of two from 512 through 32768.
- UUID must be 16 lowercase hexadecimal bytes unless set to `random`.
- VSID/full VSID must fit UDF dstring size limits.
- Owner/organization/contact use 36-byte dstring buffers.
- App ID and implementation ID are at most 23 bytes, must be 7-bit ASCII, and if nonempty must start with `*`.
- Charset options must be the first argument because identifier options are encoded during parsing.
- Requires exactly a device argument, plus optional new label.

## Research Notes

The parser is stateful: `--uuid`/`--vsid` clear pending full VSID, while `--fullvsid` clears pending UUID/VSID. This ensures `main.c` receives a single effective Volume Set Identifier update mode.
