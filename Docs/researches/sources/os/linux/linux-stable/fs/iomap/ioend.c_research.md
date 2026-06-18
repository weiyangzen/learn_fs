# File Research: sources/os/linux/linux-stable/fs/iomap/ioend.c

Manages iomap ioend allocation, writeback submission, completion, merging, sorting, and splitting.

Key paths:
- `iomap_init_ioend()` initializes the embedded-bio ioend state.
- `iomap_add_to_ioend()` appends dirty folio ranges to the current writeback ioend or submits/allocates a new one. It tags unwritten, shared, dropbehind, and boundary ioends and clamps append writeback size to in-core EOF for crash consistency.
- `iomap_ioend_writeback_submit()` submits buffered writeback bios and generates integrity metadata when needed.
- `iomap_finish_ioend()` dispatches final completion to direct I/O, buffered read, or buffered write completion once child/split refs drain.
- `iomap_finish_ioends()` drains merged ioends in task context and yields after large batches.
- `iomap_ioend_try_merge()` merges adjacent write ioends with compatible flags, status, logical offsets, and physical sectors.
- `iomap_split_ioend()` splits large ioends, including zone-append hardware-limit handling, while preserving parent completion accounting.

Error handling:
- Buffered write errors are bounced to `failed_ioend_work` to avoid nested lock acquisition in fs error reporting.
- Completion reports buffered write fs errors per folio and sets mapping errors.
- Direct ioends complete through `iomap_finish_ioend_direct()` in `direct-io.c`.

Important invariants:
- Reads are not merged because there is no useful batched completion processing.
- Anonymous writes must not go through the ordinary submit path.
- Splits must remain filesystem-block aligned.
- `iomap_ioend_bioset` is initialized at fs initcall time with embedded `struct iomap_ioend`.
