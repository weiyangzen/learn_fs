# File Research: sources/os/linux/linux-stable/fs/ubifs/replay.c

## Summary
Implements UBIFS journal replay at mount time: log scanning, bud discovery, bud recovery/authentication, replay-entry construction, sequence sorting, TNC application, and lprops/write-buffer reconstruction.

## Key APIs
- `ubifs_validate_entry()`.
- `ubifs_replay_journal()`.

## Important Behavior
Replay starts by marking the index head LEB as taken and checking that `ihead_offs` matches lprops free space. It then scans log LEBs from the master log head, requiring the first current log node to be a commit-start node with the current commit number. Reference nodes add buds to `c->buds` and to a replay list, while validating journal head, LEB, and offset ranges.

Each bud is scanned, or recovered if it is the last bud in its journal head during recovery. The code includes a compatibility quirk for old UBIFS images where the previous bud may be treated as last if the following bud is empty.

Authenticated mounts verify bud contents against authentication nodes. Unauthenticated tail nodes are accepted only on the last bud, where a power cut may have occurred; unauthenticated nodes on non-last buds fail.

Bud nodes are converted to `replay_entry` records. Inode nodes with zero link count become deletion entries; dent/xent nodes are name-bearing entries validated by `ubifs_validate_entry()`; truncation nodes become synthetic truncation keys; data nodes track recovered size. Replay entries are sorted by sequence number before being applied to the TNC.

Application handles name-key add/remove, inode-wide deletion, truncation range deletion, normal key add/remove, O_TMPFILE relink detection, and size-recovery accumulation. After replay, bud lprops are updated with computed free/dirty space and journal write buffers are positioned at bud ends.

## Dependencies
Uses log scanning/recovery, authentication hash/HMAC state, TNC add/remove APIs, lprops dirty lookup/update, journal head write buffers, UBIFS key helpers, and size recovery in `recovery.c`.

## Risks
Replay order is sequence-number critical. Dirty/free accounting for buds must handle GC’d buds whose committed lprops are stale. Authentication accepts unauthenticated nodes only for legitimate last-bud power-cut windows. Entry validation protects TNC from malformed dent/xent/truncation nodes.
