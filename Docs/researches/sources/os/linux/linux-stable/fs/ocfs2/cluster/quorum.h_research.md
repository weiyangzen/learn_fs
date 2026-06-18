# File Research: sources/os/linux/linux-stable/fs/ocfs2/cluster/quorum.h

## Summary
Declares the O2CB quorum lifecycle and event API.

## Main Responsibilities
- Expose init/exit functions.
- Expose heartbeat up/down/still-up event hooks.
- Expose connection up/error event hooks.
- Expose disk timeout fencing hook.

## Key Interfaces
- Heartbeat code calls the heartbeat-related hooks.
- Network code calls connection-related hooks.
- Heartbeat write timeout calls `o2quo_disk_timeout()`.

## Risks
Callers must deliver paired state transitions accurately; quorum correctness depends on event ordering and hold release.
