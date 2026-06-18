# File Research: sources/os/plan9/plan9/sys/src/cmd/scuzz/sense.c

Sense-data formatter for scuzz.

Key behavior:
- Maps SCSI sense key values to human-readable descriptions.
- Uses `scsierror()` from libdisk to decode additional sense code and qualifier.
- Prints the sense key, optional detailed text, and raw sense bytes to global `bout`.

Important details:
- Prints `8 + sense[7]` bytes, matching fixed-format sense additional length.
- Relies on `/sys/lib/scsicodes` indirectly through libdisk.

Filesystem relevance:
- Indirect: diagnostic support for failures returned by raw SCSI device requests.
