# File Research: sources/os/plan9/plan9/sys/src/cmd/fossil/fs.c

Top-level filesystem controller for opening, closing, snapshotting, archiving, syncing, and periodic maintenance.

`fsOpen` opens the disk, builds the cache, reads the superblock, opens the root source/file tree, and in write mode starts metadata flushing, snapshot scheduling, and archiving. It can repair an old copy-on-write root on open by copying the root block and updating the superblock with correct dependencies.

Snapshots are implemented by freezing operations with the epoch lock, bumping the epoch, forcing copy-on-write to source-entry blocks, creating a snapshot directory under `/snapshot` or `/archive`, and linking source entries into it. The file also manages low-epoch cleanup, snapshot removal, qid allocation, `vac` root construction for Venti-exported paths, halt/unhalt, and periodic snapshot/archive policy.
