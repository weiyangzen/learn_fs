# File Research: sources/os/bsd/freebsd-src/sbin/hastd/metadata.c

Read completely: 224 lines.

This file reads and writes the fixed-size on-disk HAST metadata block at the beginning of a local provider.

Key responsibilities:
- Opens and probes the local provider on first metadata read through `provinfo()`.
- Optionally takes an exclusive nonblocking `flock()` for read/write metadata access.
- Reads `METADATA_SIZE` bytes from offset 0 and decodes them as an NV buffer.
- Validates that any stored `resource` name matches the configured resource.
- Populates data size, extent size, dirty extent retention, data offset, resource UUID, local/remote generation counters, and previous role.
- Serializes current metadata fields into an NV buffer, pads to `METADATA_SIZE`, and writes it to offset 0.

Important interactions:
- Uses the local `nv` encoder/decoder and `ebuf`.
- Uses `role2str()` and provider helpers from shared HAST support code.
- Primary metadata writes are protected by `metadata_lock` in `primary.c`.

Reliability and security notes:
- Partial metadata reads/writes are treated as failure.
- The fixed metadata size is 4096 bytes; the header notes sector size is not accounted for.
- On first open failure, the file descriptor is closed and reset to avoid leaving a half-initialized resource.
