# File Research: sources/os/plan9/9front/sys/src/9/port/memmap.c

Generic physical/firmware memory map allocator with typed regions and allocated overlays.

Key responsibilities:
- Stores up to 256 `Mapent` records with address, size, and type.
- Adds free/typed regions through `memmapadd()`.
- Normalizes overlaps in `sort()`, where higher type values take precedence and adjacent equal regions merge.
- Marks allocations by overlaying `type|Allocated` records in `memmapalloc()`.
- Frees allocated subranges through `memmapfree()`.
- Reports next matching region and size through `memmapnext()` and `memmapsize()`.
- Dumps normalized map entries with `memmapdump()`.

Important behavior:
- Allocation can request a specific address or first-fit by type and alignment.
- `Allocated` is the high bit and is masked out from requested types before allocation.
- `sort()` can insert split tail entries while resolving overlaps, then repeats until stable.

Notable risks:
- Fixed 256-entry storage can reject complex maps or heavily fragmented allocation history.
- `memmapfree()` only succeeds when the supplied range lies inside a matching allocated entry.
