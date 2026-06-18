# File Research: sources/local-fs/dlm/dlm_controld/dlm_daemon.h

## Purpose
Central internal header for `dlm_controld`. It pulls in system, Corosync, kernel DLM, control-library, config, list, rbtree, and endian headers; defines global daemon state; declares message structures; defines lockspace/run data structures; and declares cross-module functions.

## Main Contents
- Filesystem paths for runtime, logs, and `/etc/dlm/dlm.conf`.
- Default logging modes and priorities.
- Option index enum and `struct dlm_option`, including default, CLI, file, and dynamic values plus reload/dynamic flags.
- Global daemon variables controlled by `EXTERN`, including cluster membership, quorum, node ids, misc minors, lockspaces list, fence state, plock fd/client, and run operations.
- DLM CPG message type enum covering protocol negotiation, lockspace start, plock operations, deadlock messages, fencing, helper-run requests/replies/cancel, and release-recover.
- `struct dlm_header`, the common internal CPG message header, with version, type, sender/target nodeids, global lockspace id, flags, and two message data fields.
- `struct lockspace` with config, CPG handle/fd/client, membership-change state, kernel/FS flags, plock state, resource trees, and dormant deadlock fields under `#if 0`.
- Run-command structures: `run_info`, `node_run_result`, `run`, `run_request`, and `run_reply`.
- Function prototypes for action/config/cpg/daemon/deadlock/main/member/fence/netlink/plock/logging/crc/helper modules.

## Integration Points
- Included by nearly every `dlm_controld` implementation file.
- Ties together global state ownership and cross-file contracts.
- Bridges public control protocol (`dlm_controld.h`) with internal daemon message protocol.

## Risks and Notes
- Large global-state surface makes module coupling high; many functions depend on globals rather than explicit context.
- Several deadlock fields/prototypes remain although the struct fields and active dispatch are disabled.
- `MAX_NODES` is tied to Corosync CPG member limits; mismatches with upstream Corosync would affect arrays throughout the daemon.
