# File Research: sources/virtualization/spdk/lib/iscsi/task.h

Full-file read: 170 lines.

This header defines the iSCSI task object and inline helpers.

Main contents:
- `struct spdk_iscsi_task` embeds `spdk_scsi_task` and adds iSCSI state: parent, connection, PDU, memory object, timestamp, R2T/DataSN counters, offsets, transfer progress, tag, LUN ID, poller, queue links, and subtask list.
- Inline helpers wrap `spdk_scsi_task_put`, PDU association/disassociation, BHS access, immediate/read checks, primary-task lookup, and memory-object access.
- Declares `iscsi_task_get`.

Integration points:
- Used throughout command, data-in/data-out, management, and cleanup paths in the iSCSI layer.
- PDU association increments `pdu->ref`; disassociation calls `iscsi_put_pdu`.

Risks and review notes:
- Inline BHS access assumes a task always has an associated PDU.
- Many transfer counters are protocol-sensitive; initialization and reset must stay centralized.
- `lun_id` is kept separately to survive hot-remove cases.

Testing focus:
- Read/write task state transitions.
- PDU refcount balance.
- Subtask parent/primary behavior.
