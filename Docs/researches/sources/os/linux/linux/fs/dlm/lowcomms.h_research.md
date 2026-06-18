# File Research: sources/os/linux/linux/fs/dlm/lowcomms.h

## Role

`lowcomms.h` declares the public interface from DLM mid-level communication and memory code into the low-level socket layer.

## Key Definitions

- `DLM_MIDCOMMS_OPT_LEN` is the size of a `struct dlm_opts` wrapper.
- `DLM_MAX_APP_BUFSIZE` subtracts midcomms option overhead from the socket buffer size.
- `CONN_HASH_SIZE` is 32.
- `nodeid_hash()` maps nodeids to connection buckets with `nodeid & (CONN_HASH_SIZE - 1)`.

## Exported Interface

The header exposes lifecycle functions, peer address registration, node close/shutdown, message allocation/commit/put/resend, explicit connect, socket mark update, and slab-cache factory functions.

## Important Behaviors and Invariants

Callers that successfully allocate a `struct dlm_msg` must commit or release it according to the lowcomms API contract. The simple nodeid hash assumes common cluster nodeids are sequential.

## Research Notes

Read completely. This header is tightly paired with `lowcomms.c` and is consumed by `midcomms.c`, `memory.c`, recovery, and membership code.
