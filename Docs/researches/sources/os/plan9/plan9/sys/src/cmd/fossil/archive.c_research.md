# File Research: sources/os/plan9/plan9/sys/src/cmd/fossil/archive.c

Background archiver that converts local fossil blocks into Venti content.

`archThread` watches superblock `next/current` archive fields, claims pending roots, recursively walks the snapshot tree with `archWalk`, writes blocks to Venti, builds a `vac` root, records the resulting score in `super.last`, and reports `archive vac:<score>`. It can fake temporary snapshots or entries marked `VtEntryNoArchive` by editing a private copy before sending.

When a child is successfully stored to Venti, parent entries or pointer slots are rewritten from local pseudo-scores to Venti scores. For real in-place rewrites, it marks blocks dirty, sets `BsVenti`, and schedules local unlink/close bookkeeping so archived blocks can eventually be reclaimed.
