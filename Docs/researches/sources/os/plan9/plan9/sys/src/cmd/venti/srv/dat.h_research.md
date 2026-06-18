# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/srv/dat.h

Defines core Venti server constants, disk-format sizes, magic/version values, error severities, dirty-flush stages, and the primary data structures used by the server and utilities.

Key structures include `Config`, `Part`, `DBlock`, `Lump`, `AMap`, `ArenaPart`, `Arena`, `ArenaHead`, `ClumpInfo`, `Clump`, `Index`, `ISect`, `IAddr`, `IEntry`, `IBucket`, `ZBlock`, `IFile`, `Stats`, `Graph`, `Round`, and `Bloom`.

The header documents the storage model: arena partitions contain arena logs; arenas contain clumps plus reverse clump-info directories and trailers; indexes map scores to arena addresses through bucketed index sections; Bloom filters accelerate misses; caches hold disk blocks, index entries, and lumps.

It also declares global runtime controls such as `mainindex`, `maxblocksize`, `readonly`, cache sleep knobs, scheduling flags, Bloom controls, sync/compression flags, stats, and trace identifiers.
