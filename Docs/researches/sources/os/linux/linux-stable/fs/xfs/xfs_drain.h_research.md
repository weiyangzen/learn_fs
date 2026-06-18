# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_drain.h

## Purpose
Declares the deferred intent drain mechanism and documents why scrub needs it.

## Main Types and APIs
With `CONFIG_XFS_DRAIN_INTENTS`, `struct xfs_defer_drain` contains an atomic pending count and waitqueue. The header declares drain init/free, waiter static-key enable/disable, group intent get/put, drain wait, and busy check.

## Design Notes
The documentation explains that deferred work can roll transactions and temporarily drop AG header locks while still updating related metadata. Scrub must therefore wait for both AG locks and zero active intents to avoid false corruption findings or unsafe repairs.

## Configuration Behavior
Without `CONFIG_XFS_DRAIN_INTENTS`, the drain type is empty and group intent helpers reduce to ordinary group get/put; drain waiting/busy APIs are not provided in that configuration.
