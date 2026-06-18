# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/srv/buildindex.c

Rebuilds a Venti index from arena contents in place. It loads a Venti config, optionally resets and rebuilds the Bloom filter, reopens arena partitions read-only for safety, initializes a disk block cache, starts one worker per selected index section, and starts arena-partition workers that scan clump directories.

The rebuild pipeline is organized around score-to-bucket routing. `arenapartproc()` walks each arena's `ClumpInfo` records backward, reconstructs `IEntry` records from clump metadata and arena-map addresses, skips `VtCorruptType`, marks Bloom bits, and sends entries to the responsible `ISect` worker.

`isectproc()` performs a three-pass external sort/rebucket operation over each index section: first sprays incoming entries into large sequential groups, then optionally repartitions them into minibuffers with `IPool`, then sorts each minibuffer and writes final `IBucket` blocks. Helpers convert scores to relative buckets, buckets to disk offsets, and offsets back to buckets.

Important behaviors include optional `-i` selection of index sections, `-b` Bloom rebuild, `-M` index memory budget splitting per section, and optional zeroing of unused bucket ranges. The tie-break sort prefers higher index addresses for duplicate scores, assuming lower-address duplicates may be corruption artifacts.
