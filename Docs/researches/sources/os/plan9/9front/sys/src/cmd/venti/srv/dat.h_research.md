# File Research: sources/os/plan9/9front/sys/src/cmd/venti/srv/dat.h

Central data model and constants for the Venti server storage subsystem.

Key contents:
- Defines sentinel values `TWID32`, `TWID64`, and `TWID8`.
- Defines storage geometry constants: `ABlockLog`, `ANameSize`, `MaxDiskBlock`, `PartBlank`, `HeadSize`, `MinArenaSize`, `IndexBase`, `MaxAMap`, and I/O/cache limits.
- Defines error severities and `syncarena` return bits.
- Defines on-disk magic numbers, versions, encodings, and packed structure sizes.
- Defines dirty write-order stages: `DirtyArena`, `DirtyArenaCib`, and `DirtyArenaTrailer`.
- Declares primary structs:
  - `Config`, `Part`, `DBlock`, `Lump`
  - `AMap`, `AMapN`, `ArenaPart`, `Arena`, `ArenaHead`, `ATailStats`, `AState`
  - `ClumpInfo`, `Clump`
  - `Index`, `ISect`, `IAddr`, `IEntry`, `IBucket`
  - `ZBlock`, `IFile`, `Stats`, `Graph`, `Round`, `Bloom`
- Defines stats enum `NStat` and stat indices used by HTTP graphs and caches.
- Declares global tunables and state such as `mainindex`, `maxblocksize`, `readonly`, `compressblocks`, `manualscheduling`, `ignorebloom`, and sleep times.

Notable details:
- Comments document Venti’s append-only arena model and index mapping.
- `IEntrySize` and `IBucketSize` are intentionally compact but noted as CPU-costly due to unaligned byte copying.
- `ArenaCIGSize` drives arena-summary cache group size.
