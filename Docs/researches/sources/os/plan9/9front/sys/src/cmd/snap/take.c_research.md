# File Research: sources/os/plan9/9front/sys/src/cmd/snap/take.c

Purpose: Captures live Plan 9 process state into snapshot data structures, with page deduplication.

Key routines:
- `sumr`: small 16-bit rolling checksum used for page hash buckets.
- `datapage`: interns page data by checksum and full comparison; marks all-zero pages specially.
- `readsection`: reads `/proc/<pid>/<section>` into a `Data` blob.
- `readseg`: reads memory/text bytes from an fd into 1024-byte deduplicated pages.
- `stackptr`: reads executable header and register data to locate the architecture's stack pointer.
- `snap`: reads proc metadata, optional text file, segment table, memory segments, and a reduced stack region around the stack pointer.

Integration: Called by `snap.c`; writes are handled by `write.c`.

Risks:
- Deduplication hash is weak but protected by full `memcmp`.
- Segment parsing depends on `/proc/<pid>/segment` textual layout.
- Stack capture intentionally trims the stack instead of reading the entire segment.
- Some segment array entries can remain nil if reading fails.
