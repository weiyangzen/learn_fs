# File Research: sources/local-fs/e2fsprogs/misc/uuidgen.c

## Purpose
Implements the simple `uuidgen` command-line utility that prints one DCE-compatible UUID.

## Key Elements
Parses `-t` and `-r` with `getopt`, selecting time-based generation, random generation, or the libuuid default generator. Initializes NLS when enabled, calls the selected libuuid generator into a `uuid_t`, unparses it into the canonical string buffer, prints it with a trailing newline, and returns success.

## Dependencies
Uses libuuid public APIs `uuid_generate`, `uuid_generate_time`, `uuid_generate_random`, and `uuid_unparse`, plus standard stdio/getopt and e2fsprogs NLS support.

## Behavior/Risks
If both `-t` and `-r` are supplied, the last parsed option wins because `do_type` is overwritten. Invalid options print usage and exit. Output buffer is sized to 37 bytes, matching canonical UUID text plus NUL.
