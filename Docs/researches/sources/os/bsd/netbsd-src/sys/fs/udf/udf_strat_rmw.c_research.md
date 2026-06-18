# File Research: sources/os/bsd/netbsd-src/sys/fs/udf/udf_strat_rmw.c

Read completely: 1520 lines.

Implements the packet read-modify-write UDF strategy for media that require packet/ECC-line granularity. It keeps packet-sized `udf_eccline` cache entries with bitmaps for present sectors, pending read-in sectors, dirty sectors, and error sectors, plus per-sector nested-buffer callbacks for callers waiting on subranges.

The private state includes a scheduler thread, condition variable, strategy mutex, sequential-write mutex, queues for waiting/read/write/sequential-write/idle/free ECC lines, line pools, blob pools, and a hash table by packet start sector. ECC line helpers lock/unlock lines, push/pop/unqueue lines from queues, allocate or recycle lines, and decide the next queue based on refcounts, wanted locks, read-in bits, dirty bits, wait timers, full-packet availability, and sequential-write flags.

Descriptor operations are packet-cache aware. Creating a descriptor obtains the containing ECC line, marks the sector present, clears it, and returns an in-line pointer into the packet blob. Reading a descriptor schedules packet reads if needed, waits for the target sector to become present or errored, validates tag and payload checksums, and holds an ECC-line reference for the descriptor. Writing a descriptor validates checksums, fixes node internals, marks the sector dirty, and releases the node descriptor outstanding lock state.

`udf_queuebuf_rmw()` handles ordinary reads, fixed writes, and sequential writes. Reads copy immediately from present sectors or attach caller buffers to pending sector callbacks. Fixed writes copy caller data into ECC lines, mark sectors present/dirty, and complete caller nested buffers. Sequential writes allocate logical space late, fix FIDs/metadata bitmap tags/node internals, translate logical mappings to physical packet sectors, copy data into ECC lines, mark them sequential, and complete caller buffers.

The scheduler thread promotes waiting dirty lines after a timeout, reads missing sectors before partial-packet writes, writes only full present packets, prefers current queue activity for a short interval, trims excess free lines, and tears down all lines on finish. Read callbacks populate missing sectors and satisfy waiting buffers. Write callbacks clear dirty bits or mark sector errors. The blob pool uses wired kernel memory sized to the packet blob.

Risk areas are concurrency and packet correctness. The code depends on careful mutex/condition-variable discipline, line refcounts, queue membership invariants, and full-packet write guarantees. Write-error handling is mostly TODO/panic/assertion oriented; comments mention future sparable remapping. The strategy also has pressure limits for sequential-write busy lines and can block waiting for line availability.
