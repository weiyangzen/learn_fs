# File Research: sources/os/plan9/plan9/sys/src/cmd/fax/file.c

Handles fax page file creation and parsing for send/receive paths.

Key behavior:
- `setpageid()` formats spool page names as `spool/time.pid.page`.
- `createfaxfile()` creates a received page file, writes Plan 9 picture-style metadata, remote station id, and `FDCS` parameters.
- `gsopen()` recognizes Ghostscript fax output by its `PC Research, Inc` header and sets default fax geometry.
- `picopen()` parses `TYPE=ccitt-g31`, `WINDOW=`, and `FDCS=` headers from Plan 9 fax picture files.
- `openfaxfile()` tries Ghostscript format first, then picture format.

Important implementation details:
- Width values are mapped through a five-entry table to Class 2 width codes.
- Send-side page geometry is only fully validated on page one.

Risks and invariants:
- Header parsing uses simple line and comma scanning; malformed files generally set protocol/system errors.
- The code expects CCITT G31 data.
