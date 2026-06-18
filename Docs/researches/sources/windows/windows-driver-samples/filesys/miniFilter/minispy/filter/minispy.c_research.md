# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/minispy/filter/minispy.c

## Purpose
Main kernel module for the MiniSpy minifilter. It initializes global state, registers the filter, creates the user-mode communication port, logs pre/post operation activity, handles user commands, and manages optional transaction enlistment/logging.

## Global State
- `MINISPY_DATA MiniSpyData`
  - Holds driver/filter handles, communication ports, output buffer list, lookaside list, record throttling counters, logging sequence number, name query method, debug flags, and optional transaction API pointers.

- `NTSTATUS StatusToBreakOn`
  - Debug-only support for breaking on a selected name-query status.

## Initialization and Unload
- `DriverEntry`
  - Initializes logging counters and defaults.
  - Initializes output buffer list and spin lock.
  - Initializes nonpaged lookaside list for records.
  - Dynamically imports transaction APIs on Vista+ builds.
  - Reads registry parameters with `SpyReadDriverParameters`.
  - Registers the filter with `FltRegisterFilter`.
  - Builds a default security descriptor.
  - Creates a communication port named by `MINISPY_PORT_NAME`.
  - Starts filtering.
  - Cleans up partially initialized resources on failure.

- `SpyFilterUnload`
  - Closes the server communication port.
  - Unregisters filter.
  - Empties queued output records.
  - Deletes lookaside list.

- `SpyQueryTeardown`
  - Allows manual detach from a volume.

## User-Mode Communication
- `SpyConnect`
  - Accepts a single client connection.
  - Stores `ClientPort`.

- `SpyDisconnect`
  - Closes the client port.

- `SpyMessage`
  - Handles raw user-mode input/output buffers.
  - Uses try/except for user buffer access.
  - Supports:
    - `GetMiniSpyLog`: validates output buffer, alignment, and returns log records via `SpyGetLog`.
    - `GetMiniSpyVersion`: writes `MINISPY_MAJ_VERSION` and `MINISPY_MIN_VERSION`.
  - Performs explicit alignment checks because Filter Manager probing does not guarantee alignment.

## Operation Logging
- `SpyPreOperationCallback`
  - Allocates a log record with `SpyNewRecord`.
  - Attempts normalized name lookup using `MiniSpyData.NameQueryMethod`.
  - Falls back to opened name or textual no-name markers if normalized lookup fails.
  - Optionally parses names when `SPY_DEBUG_PARSE_NAMES` is set.
  - On Vista+ builds, parses ECPs for create operations.
  - Stores name/ECP data in the log record.
  - Fills operation data with `SpyLogPreOperationData`.
  - For `IRP_MJ_SHUTDOWN`, invokes post logging inline because shutdown has no post callback.
  - Otherwise passes the record as completion context and requests post callback.

- `SpyPostOperationCallback`
  - Frees the record immediately if post operation is draining.
  - Completes operation logging via `SpyLogPostOperationData`.
  - If reparse tag data is present, emits a second record containing file tag data.
  - Queues records with `SpyLog`.
  - For successful transacted creates, calls `SpyEnlistInTransaction`.

## Transaction Support
- `SpyEnlistInTransaction`
  - Compiled for Vista+.
  - No-ops if dynamic Filter Manager transaction APIs are unavailable.
  - Retrieves or creates a `MINISPY_TRANSACTION_CONTEXT`.
  - Handles races where another thread sets transaction context first.
  - Enlists with `FLT_MAX_TRANSACTION_NOTIFICATIONS`.
  - Marks context with `MINISPY_ENLISTED_IN_TRANSACTION`.
  - Logs a transaction-start-style record.

- `SpyKtmNotificationCallback`
  - Allocates a log record and records KTM transaction notifications.

- `SpyDeleteTxfContext`
  - Transaction context cleanup callback.
  - Asserts correct context type and nonzero count.

## Exception Handling
- `SpyExceptionFilter`
  - Allows expected NTSTATUS exceptions.
  - If not accessing user buffers, unexpected exceptions continue searching.
  - If accessing user buffers, the caller handles the exception.

## Research Notes
MiniSpy is a logging sample rather than a policy filter. Its core architecture is:
1. capture operation metadata in pre-op,
2. enrich it in post-op,
3. queue it to user mode,
4. optionally log transaction notifications.

The file also demonstrates careful user-buffer handling for minifilter communication ports: Filter Manager probes buffers, but MiniSpy still guards access with try/except and performs alignment checks itself.
