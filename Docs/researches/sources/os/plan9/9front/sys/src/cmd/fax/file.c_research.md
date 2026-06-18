# File Research: sources/os/plan9/9front/sys/src/cmd/fax/file.c

## Purpose
Creates received fax spool files and opens outgoing fax files in supported formats.

## Key Elements
Builds page IDs as `spool/time.pid.page`, writes Plan 9 picture-style headers for received CCITT G3 pages, detects Ghostscript fax output by its fixed header, and parses picture headers for `TYPE=ccitt-g31`, `WINDOW`, and `FDCS` metadata.

## Dependencies
Uses Bio input, Plan 9 file creation, and `Modem` fields for width, resolution, length, data format, sender ID, and validity bits.

## Behavior/Risks
Outgoing page validation requires a recognized type and width on the first page. The width table is fixed to five known fax widths. Some phone-number parsing code is disabled.
