# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/factotum/confirm.c

Factotum confirmation and need-key queue support.

Key points:
- `confirmread`/`confirmflush` expose confirmation log messages.
- `confirmqueue` queues RPC reads waiting for user confirmation and logs `confirm tag=...` messages.
- `confirmwrite` parses `tag` and `answer=yes/no`, finds the waiting RPC, records the decision, and resumes it.
- `needkeyread`/`needkeyflush`, `needkeyqueue`, and `needkeywrite` implement the parallel “need key” notification queue.

Dependencies:
- Uses `Logbuf`, `Req`, `Fsstate`, attribute parsing, and `rpcread`.

Notable behavior:
- Source explicitly notes the need-key code is a copy of the confirmation queue code.
