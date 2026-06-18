# File Research: sources/os/bsd/freebsd-src/sbin/hastd/metadata.h

Read completely: 47 lines.

This header defines the HAST metadata block size and metadata read/write API.

Key responsibilities:
- Defines `METADATA_SIZE` as 4096 bytes.
- Declares `metadata_read(struct hast_resource *, bool openrw)`.
- Declares `metadata_write(struct hast_resource *)`.

Important interactions:
- Included by primary/secondary role code and metadata implementation.
- Depends on `struct hast_resource` from `hast.h`.

Reliability notes:
- The comment flags a known limitation: metadata sizing does not account for actual provider sector size.
