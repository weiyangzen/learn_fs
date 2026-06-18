# File Research: sources/os/plan9/9front/sys/src/cmd/gzip/zip.h

Defines ZIP format constants and the shared `ZipHead` structure.

Key points:
- Defines local, central, and end-central magic numbers:
  - `ZHeader`
  - `ZCHeader`
  - `ZECHeader`
- Defines general-purpose flag bits:
  - `ZEncrypted`
  - `ZTrailInfo`
  - `ZCompPatch`
- Defines ZIP CRC polynomial `ZCrcPoly`.
- Defines compression method `ZDeflate = 8`.
- Defines internal text attribute and OS identifiers for version fields.
- Defines DOS external attribute flags, including read-only, hidden, system, volume label, directory, and archive.
- Defines byte sizes/offsets for local headers, trailers, central headers, and end-central headers.
- `ZipHead` stores version info, flags, method, timestamps, CRC, compressed/uncompressed sizes, attributes, local-header offset, and filename.

Dependencies and interactions:
- Shared by `zip.c` and `unzip.c`.
- Encodes exactly the subset of ZIP metadata those tools read/write.

Research relevance:
- The common ZIP metadata contract for Plan 9 archive creation and extraction.
