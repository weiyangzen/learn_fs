# File Research: sources/os/linux/linux-stable/fs/dlm/requestqueue.c

## Purpose
`requestqueue.c` saves normal DLM messages received while a lockspace is in recovery and replays or purges them after recovery reaches a safe point.

## Queue Entries
`struct rq_entry` stores:
- list linkage
- low 32 bits of recovery sequence
- sender node id
- copied `struct dlm_message` plus extra payload bytes

`dlm_add_requestqueue()` copies a received message into an allocated queue entry using the message header length.

## Replay
`dlm_process_requestqueue()` runs after locking is re-enabled. It processes entries in order through `dlm_receive_message_saved()`, then frees them. It clears `LSFL_RECV_MSG_BLOCKED` once the queue is empty.

The function drops and reacquires `ls_requestqueue_lock` between entries to avoid monopolizing CPU, but aborts if locking becomes stopped again.

## Purge
`dlm_purge_requestqueue()` removes messages invalidated by recovery:
- messages for removed nodes
- messages during lockspace teardown
- directory operations (`REMOVE`, `LOOKUP`, `LOOKUP_REPLY`)
- all messages in no-directory mode

## Risks and Notes
The comments describe a race with `dlm_recv` and `dlm_ls_stop()` while saved messages drain. The code keeps receive-side blocking state explicit with `LSFL_RECV_MSG_BLOCKED`.
