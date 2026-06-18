# File Research: sources/os/linux/linux/fs/dlm/requestqueue.c

## Role

`requestqueue.c` stores normal DLM messages received while locking is stopped for recovery, then replays or purges them when recovery completes.

## Queue Entry

`struct rq_entry` stores the recovery sequence low bits, sender nodeid, and a copied `struct dlm_message` plus variable extra payload.

## Queueing

`dlm_add_requestqueue()` allocates an entry with `GFP_ATOMIC`, copies the message and extra bytes, records `ls_recover_seq`, and appends it to `ls_requestqueue`.

## Replay

`dlm_process_requestqueue()` runs after normal locking has been re-enabled. It drains messages under `ls_requestqueue_lock`, logs each saved message, calls `dlm_receive_message_saved()`, frees the entry, and aborts if locking stops again.

## Purge Policy

`dlm_purge_requestqueue()` removes entries if:
- the lockspace is being freed
- the sender was removed
- the message is directory remove/lookup/lookup-reply
- the lockspace has no directory

Directory requests are purged because recovery rebuilds the directory and requesters must resend.

## Important Behaviors and Invariants

`LSFL_RECV_MSG_BLOCKED` is cleared only when the queue is empty. Receive paths can wait for this drain before processing new normal messages.

## Research Notes

Read completely. This file protects normal lock message ordering across recovery boundaries.
