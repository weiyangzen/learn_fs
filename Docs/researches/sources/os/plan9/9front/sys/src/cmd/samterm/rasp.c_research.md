# File Research: sources/os/plan9/9front/sys/src/cmd/samterm/rasp.c

Purpose: Implements samterm's `Rasp` sparse text cache. A rasp is a linked list of `Section` records, each either holding actual runes or representing a missing span whose contents must be requested from the host editor.

Key routines:
- `rinit`, `rclear`: initialize and free a rasp section list.
- `rsinsert`, `rsdelete`, `splitsect`, `findsect`: maintain section boundaries and linked-list structure.
- `rresize`: updates cached document shape after insert/delete by removing old span sections and inserting a missing span for new text.
- `rdata`: replaces missing sections with actual rune data received from the host.
- `rclean`: coalesces adjacent sections with the same known/missing state, bounded by `TBLOCKSIZE` for text sections.
- `rload`: copies available cached runes from a range into global `scratch`; intentionally skips missing spans.
- `rmissing`, `rcontig`: measure missing or contiguous known/missing coverage.
- `Strgrow`: reallocates scratch rune storage.

Integration: Depends on `samterm.h` globals such as `scratch`, `nscralloc`, `alloc`, and `panic`, plus frame/text behavior elsewhere in samterm. Host protocol handlers use this file to decide when screen data is locally available versus missing.

Risks and invariants:
- The linked list is expected to be internally consistent; bad boundaries panic.
- Missing sections have `text == 0`, while known sections own allocated rune buffers.
- `rdata` panics if asked to overwrite already-known text, enforcing host/cache sequencing.
- `rload` returns a global scratch buffer, so callers must treat the result as transient.
