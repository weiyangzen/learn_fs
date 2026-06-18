# File Research: sources/os/bsd/freebsd-src/sys/sys/bio.h

## Purpose
`bio.h` defines the kernel block I/O request object used by GEOM, disks, and lower storage layers.

## Main Interfaces
- `BIO_READ`, `BIO_WRITE`, `BIO_DELETE`, `BIO_GETATTR`, `BIO_FLUSH`, `BIO_ZONE`, and `BIO_SPEEDUP` identify I/O operations.
- `BIO_ERROR`, `BIO_DONE`, `BIO_ONQUEUE`, `BIO_ORDERED`, `BIO_UNMAPPED`, `BIO_VLIST`, `BIO_SWAP`, `BIO_EXTERR`, and speedup flags describe request state and memory layout.
- `struct bio` contains command/flags, target device/disk, offset/length/counts, data or page-array backing, completion callback, GEOM links, parent/child accounting, zone command args, timing, task callback, spare fields, optional tracking, physical block number, and extended error state.
- `struct bio_queue_head` provides queue metadata for disk sorting and batching.
- Kernel functions include `biodone`, `biofinish`, `biowait`, `bioq_*`, and `physio`.

## Implementation Notes
The structure separates consumer-private and provider-private fields and supports chained or split I/O through `bio_parent`, `bio_children`, and `bio_inbed`. `bio_error` aliases the embedded extended-error structure's errno field, keeping older code compatible while supporting richer error detail.

## Dependencies and Constraints
The full structure is visible only under `_KERNEL`. It depends on GEOM types, disk zone arguments, queue macros, and optional buffer tracking. `BIO_ORDERED` expresses queue ordering semantics and must be honored by providers.
