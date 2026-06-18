# File Research: sources/os/plan9/plan9/sys/src/9/port/segment.c

Implements user memory segment management and executable image caching.

Segment management:
- `initseg` initializes the image cache/free lists.
- `newseg` allocates a `Segment`, chooses inline or heap PTE map storage, and initializes semaphore list state.
- `putseg` decrements references, detaches image relationships, frees PTEs/profile/map, and releases the segment.
- `dupseg` implements rfork/fork segment duplication: text/shared/physical share; stack copies; BSS/data copy-on-write unless memory is shared.
- `data2txt` is referenced externally in `portfns.h`; this file handles the `segno == TSEG` conversion path through that helper.
- `segpage` installs a page in the right PTE slot.
- `relocateseg` adjusts page virtual addresses after stack relocation.

Image cache:
- `attachimage` finds or creates an `Image` keyed by qids/mount channel/type and attaches or creates a text segment.
- `putimage` drops image references, removes from hash, and defers channel closes into `freechan`.
- `imagereclaim` uncaches image-backed free-list pages to free image structures.
- `imagechanreclaim` closes deferred image channels outside spin locks.

Address-space operations:
- `ibrk` grows/shrinks a segment, checking overlap and resizing PTE maps.
- `mfreeseg` removes PTEs over a range, delays actual `putpage` until after TLB flush for shared segments.
- `isoverlap` detects address overlap.
- `segattach` attaches named physical/shared/memory segments, choosing an address hole when `va == 0`.
- `addphysseg` and `isphysseg` manage attachable physical segment types.

Other:
- `syssegflush` marks pages for text-cache flush and flushes MMU.
- `segclock` updates text segment profiling counters.

Cautions:
- `putimage` defers channel close because close can block and must not happen under spin locks.
- `segattach` excludes `ESEG` and protects the zero page by rejecting/avoiding `va == 0`.
