# File Research: sources/virtualization/qemu/block/replication.c

Implements the `replication` block filter used by block replication/failover flows. It has primary and secondary modes and tracks stages: none, running, failover, failover failed, and done. The filter registers `ReplicationOps` callbacks for start, checkpoint, get-error, and stop.

Primary mode is minimal: it is used to forward write requests and records errors while returning success to the caller. Secondary mode expects a three-layer chain: active disk, hidden disk, and secondary disk. On start it validates backing topology and equal lengths, ensures active/hidden disks can be emptied, temporarily reopens hidden/secondary writable, attaches them as children, blocks operations on a configured top node, and starts an internal backup job from secondary to hidden.

Checkpoints on the secondary call `backup_do_checkpoint()`, then empty both active and hidden disks. Reads are only allowed on secondary; writes either go to the active disk during normal running or, after failed failover, split writes between already allocated active/hidden regions and the secondary base to preserve consistency.

Stopping secondary replication cancels the backup job, optionally checkpoints for non-failover stop, or starts an active commit from the active disk into the secondary disk during failover. `replication_done()` marks success, detaches hidden/secondary children, and clears error state; failure moves to `BLOCK_REPLICATION_FAILOVER_FAILED`. Close cancels active jobs and unregisters replication state.
