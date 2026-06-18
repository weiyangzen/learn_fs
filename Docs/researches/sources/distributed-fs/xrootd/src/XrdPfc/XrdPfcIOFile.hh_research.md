# sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcIOFile.hh

## Purpose
Declares `IOFile`, the whole-file cache IO implementation. It adapts the XRootD cache interface to the shared `File` object that stores a remote file in one local data file plus `.cinfo`.

## Important APIs, Types, and Functions
- `HasFile()`, `Fstat()`, and `FSize()` expose file availability and size/stat information.
- Overrides sync/async `Read`, `pgRead`, sync/async `ReadV`, `Update`, `ioActive`, and `DetachFinalize`.
- Private `ReadBegin`/`ReadEnd` and `ReadVBegin`/`ReadVEnd` centralize validation, expected-size tracking, callback forwarding, and active-read accounting.
- `initialStat()` is used during file acquisition to resolve size from local metadata or upstream IO.

## Control Flow
Public read methods create an internal response handler and call the begin/end helper pair. `Update` refreshes the base upstream IO and informs the `File` so remote location metadata remains current. Detach checks are delegated to `File::ioActive`.

## State and Persistence Behavior
Only runtime state is `File *m_file`. The pointed-to `File` owns persistence and metadata state. `IOFile` lifetime is tied to detach finalization.

## Dependencies and Integration Points
Includes `XrdPfcIO.hh`, `XrdPfc.hh`, `Stats`, and `XrdPfcFile.hh`. It is used by the proxy cache attach path for normal non-HDFS/block-split objects.

## Risks and Test Signals
Risks are mostly lifecycle-related: null `m_file`, duplicate finalization, read callbacks after detach, and construction-time `Fstat` behavior. Tests should include failed `GetFile`, detach during async read, and Update propagation.
