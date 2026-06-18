# File Research: sources/virtualization/spdk/lib/iscsi/task.c

Full-file read: 82 lines.

This file allocates and frees iSCSI task objects backed by the global task mempool.

Main responsibilities:
- `iscsi_task_get` obtains a task from `g_iscsi.task_pool`, zeroes it, timestamps it, associates it with a connection, increments pending-task counters, and constructs the embedded `spdk_scsi_task`.
- Parent/subtask initialization copies SCSI metadata and transfer state from the parent and increments parent refcount.
- `iscsi_task_free` handles histogram tallying, parent release, data-in counter decrement, mobj return, PDU disassociation, pending-task decrement, and mempool return.

Integration points:
- Wraps SPDK SCSI task lifecycle via `spdk_scsi_task_construct`.
- Uses target histograms from `tgt_node.c` and PDU/data-pool helpers from the iSCSI connection/subsystem layer.

Risks and review notes:
- Mempool exhaustion aborts the process.
- Histogram access assumes target lifetime and histogram pointer stability while the task is freed.
- Parent/subtask refcount and `data_in_cnt` counters must stay balanced.

Testing focus:
- Parent/subtask free ordering.
- Histogram tally on task completion.
- PDU/mobj cleanup paths.
