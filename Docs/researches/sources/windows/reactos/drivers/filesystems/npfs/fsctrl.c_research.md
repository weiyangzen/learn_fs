# File Research: sources/windows/reactos/drivers/filesystems/npfs/fsctrl.c

## Purpose
Implements NPFS filesystem-control operations, including pipe listen/disconnect, peek, transceive, wait, impersonation, and client-process metadata.

## Main Responsibilities
- Unimplemented internal/event controls:
  - `NpInternalTransceive`
  - `NpInternalRead`
  - `NpInternalWrite`
  - `NpAssignEvent`
  - `NpQueryEvent`
- Client process metadata:
  - `NpQueryClientProcess` reports `Ccb->ClientSession` or `Ccb->Process`.
  - `NpSetClientProcess` is restricted to kernel callers and replaces the CCB client-session blob.
- Pipe controls:
  - `NpImpersonate` impersonates the client from the server end.
  - `NpDisconnect` server-only disconnects a pipe and clears security.
  - `NpListen` server-only transitions to listening or queues the listen IRP.
  - `NpPeek` reports pipe state, bytes available, message count/length, and optionally copies queued data without consuming it.
  - `NpTransceive` writes a message and then queues the same IRP as a read for the response.
  - `NpWaitForNamedPipe` waits on the root handle until a named pipe has a listening instance.
- `NpCommonFileSystemControl` dispatches FSCTLs and chooses shared vs exclusive VCB locking.
- `NpFsdFileSystemControl` wraps dispatch in `FsRtlEnterFileSystem` and completes non-pending IRPs.

## Important Interactions
- Uses read/write queue helpers for peek and transceive.
- Uses `statesup.c` for listen/disconnect transitions.
- Uses `waitsup.c` for `FSCTL_PIPE_WAIT`.
- Uses `secursup.c` for server-side impersonation.
- Uses event-buffer fields, but actual event assignment/query and generic-table callbacks are not implemented elsewhere.

## Notable Behavior
- `NpTransceive` requires a connected full-duplex pipe and message read mode.
- `NpWaitForNamedPipe` currently has alias translation commented out.
- `NpPeek` allows peeking a closing pipe only if queued write data remains.

## Risks / Review Notes
- Several FSCTLs return `STATUS_NOT_IMPLEMENTED`; this is a major compatibility gap.
- `NpSetClientProcess` allocates `ClientSession` but does not check allocation failure before copying.
- `NpTransceive` allocates a secondary IRP for partially written input; error paths around allocated buffers and queued IRPs are sensitive.
