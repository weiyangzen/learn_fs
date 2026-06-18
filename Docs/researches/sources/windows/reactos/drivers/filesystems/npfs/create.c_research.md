# File Research: sources/windows/reactos/drivers/filesystems/npfs/create.c

## Purpose
Implements NPFS create/open handling for the named-pipe filesystem, including opening the filesystem object/root directory, creating server pipe instances, opening client ends, resolving aliases, enforcing security/share rules, and waking deferred wait/notify IRPs.

## Main Responsibilities
- `NpFsdCreate` handles normal `IRP_MJ_CREATE` opens:
  - Opens `\Device\NamedPipe` itself when no name is supplied.
  - Opens the root DCB for `\`.
  - Translates aliases through `NpTranslateAlias`.
  - Uses `NpFindPrefix`/`NpFindRelativePrefix` to locate an existing FCB.
  - Connects a client to a listening server-side CCB with `NpCreateClientEnd`.
- `NpFsdCreateNamedPipe` handles `IRP_MJ_CREATE_NAMED_PIPE`:
  - Locates an existing pipe FCB or creates a new one under the root DCB.
  - Creates a server-side CCB in `FILE_PIPE_LISTENING_STATE`.
- `NpCreateClientEnd`:
  - Performs `SeAccessCheck` against the FCB security descriptor.
  - Rejects access incompatible with inbound/outbound pipe configuration.
  - Finds a listening CCB and moves it to connected state.
  - Initializes client impersonation/security state.
- `NpCreateExistingNamedPipe`:
  - Validates access, instance limits, create disposition, and share mode.
  - Adds another server instance for an existing named pipe.
  - Cancels `FSCTL_PIPE_WAIT` waiters via `NpCancelWaiter`.
- `NpCreateNewNamedPipe`:
  - Validates timeout, max instances, share mode, and byte/message mode combinations.
  - Allocates an FCB/CCB and assigns/logs a security descriptor.
- `NpTranslateAlias`:
  - Uses global alias lists built by `main.c`.
  - Upcases pipe names and substitutes matching target names.

## Important Interactions
- Depends on `strucsup.c` for FCB/CCB/root allocation and deletion.
- Depends on `prefxsup.c` for prefix matching.
- Depends on `statesup.c` for state transitions to connected/listening.
- Depends on `secursup.c` and `seinfo.c` conventions for security descriptors and client contexts.
- Uses the common NPFS deferred completion pattern: collect IRPs on `DeferredList`, release the VCB lock, then call `NpCompleteDeferredIrps`.

## Notable Behavior
- The VCB lock is acquired exclusively for all create operations because prefix tables, FCB lists, CCB lists, and waiter/notify queues can change.
- Server create derives pipe direction from share access:
  - read+write share => full duplex
  - read share => outbound
  - write share => inbound
- New named pipes require a specified negative timeout and nonzero max instance count.
- Client opens fail with `STATUS_PIPE_NOT_AVAILABLE` when no CCB is listening.

## Risks / Review Notes
- `NpCheckForNotify` contains `ASSERT(IsListEmpty(ListHead))` immediately before looping while the list is non-empty. That assertion appears contradictory if notify IRPs are expected to be completed.
- Alias translation mutates the local `FileName` copy, not the file object name itself, which is intentional for lookup but important for later diagnostics.
- Existing-pipe create requires exact share access matching the pipe configuration; this is strict and should be compared with Windows behavior if compatibility issues appear.
