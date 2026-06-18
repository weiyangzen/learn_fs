# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/shutdown.c

This file implements filesystem shutdown handling through `Ext2ShutDown`.

The function acquires the global Ext2 resource exclusively, iterates `Ext2Global->VcbList`, acquires each mounted VCB's main resource, updates and caps the superblock mount count, saves the superblock, flushes dirty file caches, flushes the volume stream, and sends shutdown to the underlying disk.

If the global resource cannot be acquired with the IRP context wait policy, it returns `STATUS_PENDING` and queues the request.

Failures during flush call `DbgBreak` except media write-protection on volume flush. Completion and cleanup are centralized in the SEH finally block.

Research notes: this is a global coordination path with strong locking; it assumes the VCB list remains stable under `Ext2Global->Resource`.
