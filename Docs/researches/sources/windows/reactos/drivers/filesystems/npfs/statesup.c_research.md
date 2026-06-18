# File Research: sources/windows/reactos/drivers/filesystems/npfs/statesup.c

## Purpose
Implements named-pipe state transitions: listening, connected, disconnected, closing, and close cleanup behavior.

## Main Responsibilities
- `NpCancelListeningQueueIrp` cancels a pending listen IRP.
- `NpSetConnectedPipeState`:
  - Converts a listening CCB to connected.
  - Sets default client read/completion modes.
  - Binds the client file object.
  - Completes queued listen IRPs successfully.
- `NpSetDisconnectedPipeState`:
  - Handles transitions from disconnected/listening/connected/closing.
  - Drains queues with `STATUS_PIPE_DISCONNECTED`.
  - Clears client event buffer, client file object, security, and client session.
- `NpSetListeningPipeState`:
  - Cancels waiters for newly available pipe instances.
  - Returns `STATUS_PIPE_LISTENING` in complete-operation mode.
  - Otherwise queues the listen IRP pending cancellation/connection.
- `NpSetClosingPipeState`:
  - Handles final close for server or client ends.
  - Drains affected queues with `STATUS_PIPE_BROKEN`.
  - Clears file objects.
  - Deletes CCB and possibly FCB when no instances remain.
  - Signals event buffers on connected-to-closing transition.

## Important Interactions
- Called by create, fsctl listen/disconnect, cleanup/close paths outside this group, and queue support.
- Uses `NpDeleteCcb`, `NpDeleteFcb`, `NpRemoveDataQueueEntry`, and wait cancellation.

## Risks / Review Notes
- Switch fallthroughs are intentional and documented by comments; changes here require care.
- Event-buffer deletion depends on event-table support, which is stubbed in `strucsup.c`.
- Closing state drains only selected queues depending on which pipe end closes.
