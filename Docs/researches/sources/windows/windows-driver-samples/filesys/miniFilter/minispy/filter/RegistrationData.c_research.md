# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/minispy/filter/RegistrationData.c

## Purpose
Contains MiniSpy’s static Filter Manager registration data in a separate file so it can be placed in the `INIT` segment.

## Operation Registration
Registers MiniSpy’s generic pre/post callbacks for broad coverage across IRP and fast-I/O style operations, including:
- create, create named pipe, create mailslot
- close, cleanup
- read, write
- query/set file information
- query/set EA
- flush buffers
- query/set volume information
- directory control
- filesystem/device/internal-device control
- lock control
- security and quota operations
- PNP
- section synchronization and cache-manager callbacks
- fast I/O check
- network query open
- MDL read/write operations
- volume mount/dismount

`IRP_MJ_SHUTDOWN` has only a pre-operation callback because post-operation callbacks are not supported for shutdown.

## Context Registration
- If `MINISPY_VISTA` is true, registers `FLT_TRANSACTION_CONTEXT` with:
  - cleanup callback `SpyDeleteTxfContext`
  - size `sizeof(MINISPY_TRANSACTION_CONTEXT)`
  - tag `'ypsM'`
- Ends with `FLT_CONTEXT_END`.

## Filter Registration
- Uses `FLT_REGISTRATION_VERSION`.
- On Windows 8 and later, uses `FLTFL_REGISTRATION_SUPPORT_NPFS_MSFS`.
- Supplies:
  - `Contexts`
  - `Callbacks`
  - `SpyFilterUnload`
  - `SpyQueryTeardown`
- No instance setup or teardown start/complete callbacks.
- No name provider callbacks.
- If Vista transaction support is compiled, supplies `SpyKtmNotificationCallback`.

## Section Placement
When `ALLOC_DATA_PRAGMA` is defined:
- data and const data are placed in `INIT`
- section settings are restored at the end

## Research Notes
This file is declarative. MiniSpy’s behavior is centralized in generic callbacks; this registration table makes MiniSpy observe nearly every meaningful file-system operation rather than implementing operation-specific callbacks.
