# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbtransaction.c

Provides generic SMB transaction and transaction2 decode, encode, response, datagram send, and client execution machinery.

Key points:
- `_smbtransactiondecodeprimary` parses primary transaction requests, validates counts/offsets, copies parameter and data fragments, and returns whether the transaction is complete.
- `decoderesponse`, `smbtransactiondecoderesponse`, and `smbtransactiondecoderesponse2` assemble multi-fragment transaction responses into output buffers.
- `_transactionencodeprimary` constructs primary transaction requests and packs as much parameter/data payload as fits.
- `_transactionencoderesponse` constructs one response fragment and advances output buffer read positions.
- `smbtransactionrespond` sends one or more response fragments.
- `smbtransactionexecute` sends a request, optionally handles secondary requests, receives response fragments, validates headers/errors, and decodes results.

Dependencies:
- Uses `SmbTransaction`, `SmbHeader`, `SmbPeerInfo`, `SmbBuffer`, and pluggable `SmbTransactionMethod` callbacks.

Notable behavior:
- Secondary transaction support is required only when the primary packet cannot carry all parameters/data.
- There is a defective `goto toosmall` loop in `_transactionencoderesponse` where the error label jumps to itself after setting the error string.
