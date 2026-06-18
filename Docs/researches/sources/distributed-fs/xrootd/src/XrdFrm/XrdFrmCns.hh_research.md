<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmCns.hh -->
# sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmCns.hh

## Purpose
`XrdFrmCns.hh` declares the static CNS notification facade used by FRM code. It exposes create, remove-file, remove-directory, and initialization APIs while hiding FIFO path management and write retry logic in `XrdFrmCns.cc`.

## Important APIs
`Add(tID, Path, Size, Mode)` sends create/close-write events. `Rm(Path, islfn)` and `Rmd(Path, islfn)` send file and directory removal events only when CNS mode is enabled. `cnsAuto`, `cnsIgnore`, and `cnsRequire` describe runtime mode. Two `Init()` overloads either preset path/mode from config or complete process-specific initialization with headers.

## Control Flow And State
All members and helper methods are static. Private state includes event path, delete headers, header length, initialization state, file descriptor, and mode. Header constants distinguish directory and file removal records.

## Dependencies And Integration Points
The header depends on POSIX `uio` types for vector writes. It is included by configuration and unlink/admin code. Public methods are intentionally process-global, matching a single CNS endpoint per FRM process.

## Risks And Test Signals
Because API state is static, reconfiguration and repeated `Init()` calls must be tested to ensure paths and headers are refreshed correctly. `Rm` and `Rmd` silently do nothing in ignore mode, which is expected but needs integration coverage. Tests should validate mode constants, `islfn` behavior, and that remove calls before complete initialization either initialize lazily or log a controlled failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmCns.hh -->
