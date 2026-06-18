# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbcomtransaction.c

Server handlers for `SMB_COM_TRANSACTION` and `SMB_COM_TRANSACTION2`.

Key functions:
- `sendresponse` adapts `smbresponsesend` for transaction method callbacks.
- `smbcomtransaction` decodes a primary transaction, handles secondary continuation state, allocates output buffers, dispatches `/PIPE/LANMAN` to `smbrap2`, and encodes transaction responses.
- `smbcomtransaction2` decodes transaction2, validates setup count/opcode, dispatches through `smbtrans2optable`, and encodes transaction2 responses.

Interactions:
- Uses transaction encode/decode/execute/respond functions declared in `smbfns.h`.
- RAP2 implementation lives in `smbrap2.c`.

Notable details:
- Sets `s->nextcommand` to require the appropriate secondary command when decode reports an incomplete transaction.
