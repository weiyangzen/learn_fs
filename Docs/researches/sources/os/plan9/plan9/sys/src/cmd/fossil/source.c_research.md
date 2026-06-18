# File Research: sources/os/plan9/plan9/sys/src/cmd/fossil/source.c

This file implements Fossil’s `Source` abstraction: a locked handle over a Venti/Fossil `Entry` and its block tree. It validates entries, opens roots and child sources, creates/removes/truncates sources, tracks directory entry counts, and reads/updates entry metadata.

The core behavior is copy-on-write block walking. `_sourceBlock` computes pointer indexes for a block number, grows pointer depth when needed, and uses `blockWalk` to fetch or copy blocks into the current epoch. `sourceGrowDepth`, `sourceShrinkDepth`, and `sourceShrinkSize` maintain the Venti pointer tree and remove stale local links.

Locking is coupled to block references: `sourceLock` loads the block containing the source entry and stores it in `r->b`; `sourceUnlock` releases it. `sourceLock2` special-cases siblings in the same entry block and orders locks to reduce deadlock risk.

Snapshot handling appears in `sourceAlloc`, `sourceLoadBlock`, and `_sourceBlock`: writable opens reject snap entries, read-only snapshot sources enforce epoch windows, refresh stale local labels by rewalking from the parent, and reject `VtEntryNoArchive` data for snapshot reads.

Notable observation: `sourceShrinkDepth` contains an explicit `BUG` comment questioning `type++`, so depth-shrink behavior is a known sensitive area.
