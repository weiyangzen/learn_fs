# File Research: sources/os/plan9/9front/sys/src/cmd/aux/flashfs/journal.c

Role: Flashfs journal loader, writer, sector allocator, and compactor.

Generations and sectors:
- Maintains two `Gen` structures, each a linked sequence of `Sect` records with generation number, sequence range, and optional duplicate sector.
- Free sectors are tracked in a linked list; bad sectors abort load.
- Active generation parity is `eparity`; summarization copies live data into the alternate generation.

Recovery:
- `loadfs` scans all sectors for magic, groups sectors into two generations, detects free/bad sectors, handles missing second generation, duplicate high sequence sectors, and generation ordering.
- `checkdata` and `checksweep` repair documented interruption windows around copying, summaries, and generation sweep.
- `load1` replays journal records into the entry tree, reconstructing metadata and extents.

Writing:
- `sputw` appends a record by first writing payload after the current offset, optionally writing file data, then committing the type byte last. On write failure it duplicates the sector.
- `put` and `putw` append metadata-only and data-carrying records to the active tail sector.
- `need` ensures space exists, triggers summarization if free sectors are low, allocates new sectors, or flips readonly on generation-full failure.

Compaction:
- `summarize` walks old sectors, preserves only live entries/extents, emits summary begin/end markers, frees old sectors, and swaps generations when a generation drains.

Time handling:
- `now` keeps timestamps monotonic by adding and gradually draining a `delta` if filesystem times are ahead of system time.

Limits:
- Usable flash limit is set to 80 percent of total sectors.
- `maxwrite` is bounded by sector room and `WRSIZE` (4 KiB).
