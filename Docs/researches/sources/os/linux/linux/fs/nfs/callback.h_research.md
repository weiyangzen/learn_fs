# File Research: sources/os/linux/linux/fs/nfs/callback.h

## Purpose
Defines NFSv4 callback protocol constants, argument/result structures, callback processing state, and public callback function prototypes.

## Main Contents
- Callback RPC program number and buffer sizes.
- Callback procedure numbers: `CB_NULL` and `CB_COMPOUND`.
- `struct cb_process_state`, carrying resolved client, session slot, net namespace, minor version, DRC status, and referring-call count.
- Argument/result structures for callback operations:
  - `CB_GETATTR`
  - `CB_RECALL`
  - `CB_SEQUENCE`
  - `CB_RECALL_ANY`
  - `CB_RECALL_SLOT`
  - `CB_LAYOUTRECALL`
  - `CB_NOTIFY_DEVICEID`
  - `CB_NOTIFY_LOCK`
  - `CB_OFFLOAD` when NFSv4.2 is enabled.
- Recall-any type mask constants.
- Callback service lifecycle declarations.

## Important Constants
- `NFS4_CALLBACK`
- `NFS4_CALLBACK_XDRSIZE`
- `NFS4_CALLBACK_BUFSIZE`
- `NFS41_BC_MIN_CALLBACKS`
- `NFS41_BC_MAX_CALLBACKS`
- `NFS4_MIN_NR_CALLBACK_THREADS`

## Integration Points
Included by `callback.c`, `callback_proc.c`, and `callback_xdr.c`. It also exposes callback up/down functions to NFSv4 client setup code.

## Notable Details
- `cb_process_state.clp` is always set directly for v4.0 and set by `CB_SEQUENCE` for v4.1+.
- The callback DRC status field is used to propagate replay/cache errors through later operations in a compound.
- Backchannel concurrency constants document the current single-slot callback model.
