# File Research: sources/os/plan9/plan9/sys/src/cmd/gzip/zip.h

Shared ZIP-format constants and `ZipHead` structure.

- Defines local header, central directory header, and end-of-central-directory magic numbers.
- Defines general-purpose flag bits such as encryption and trailer/data-descriptor presence.
- Defines CRC polynomial, deflate method ID, file-attribute OS IDs, DOS external attribute bits, and fixed header sizes/offsets.
- `ZipHead` stores version/OS metadata, flags, method, DOS time/date, CRC, sizes, attributes, local-header offset, and filename.

Used by both `zip.c` and `unzip.c` as the local ZIP metadata contract.
