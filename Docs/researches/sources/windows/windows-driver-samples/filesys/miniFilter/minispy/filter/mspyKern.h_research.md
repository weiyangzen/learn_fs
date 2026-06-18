# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/minispy/filter/mspyKern.h

## Purpose
Kernel-only MiniSpy header. It defines version/platform feature macros, internal global state, transaction support types, constants, and prototypes for MiniSpy’s kernel modules.

## Includes and Tags
- Includes:
  - `<fltKernel.h>`
  - `<suppress.h>`
  - `"minispy.h"`
- Defines allocation tag:
  - `SPY_TAG 'ypSM'`

## Platform Feature Macros
- `MINISPY_WIN8`
  - Windows 8+ behavior, including NPFS/MSFS registration support.
- `MINISPY_WIN7`
  - Windows 7+ ECP support.
- `MINISPY_VISTA`
  - Vista+ transaction and older ECP support.
- `MINISPY_NOT_W2K`
  - Excludes Windows 2000 behavior paths.

## Vista+ Transaction and ECP Support
When `MINISPY_VISTA` is true:
- Defines dynamic Filter Manager API function pointer types:
  - `PFLT_SET_TRANSACTION_CONTEXT`
  - `PFLT_GET_TRANSACTION_CONTEXT`
  - `PFLT_ENLIST_IN_TRANSACTION`
- Defines known ECP type flags:
  - prefetch
  - oplock key
  - NFS
  - SRV
- Defines `ECP_TYPE` enumeration.
- Defines `ADDRESS_STRING_BUFFER_SIZE`.

## Global Data Structure
`MINISPY_DATA` contains:
- driver object and filter handle
- server and client communication ports
- output buffer list and spin lock
- nonpaged lookaside list for records
- record allocation throttling fields
- static out-of-memory record buffer
- log sequence counter
- configured name query method
- debug flags
- dynamically imported transaction API pointers on Vista+ builds

## Transaction Context
`MINISPY_TRANSACTION_CONTEXT`
- `Flags`
- `Count`

`MINISPY_ENLISTED_IN_TRANSACTION` marks contexts that have successfully enlisted.

## Defaults and Registry Names
- `DEFAULT_MAX_RECORDS_TO_ALLOCATE`
- `MAX_RECORDS_TO_ALLOCATE`
- `DEFAULT_NAME_QUERY_METHOD`
- `NAME_QUERY_METHOD`
- `SPY_DEBUG_PARSE_NAMES`

## Prototypes
Declares:
- operation callbacks
- KTM transaction callback
- unload and teardown callbacks
- registry parameter loading
- exception filter
- buffer allocation/free routines
- log record allocation/free routines
- ECP parsing and record name helpers
- operation and transaction logging routines
- user-mode log retrieval
- output queue draining
- transaction context cleanup

## Research Notes
This header is the internal contract tying together MiniSpy’s registration, logging, communication, and transaction code. It also preserves compatibility across OS versions by compiling feature blocks conditionally and dynamically importing newer Filter Manager transaction APIs.
