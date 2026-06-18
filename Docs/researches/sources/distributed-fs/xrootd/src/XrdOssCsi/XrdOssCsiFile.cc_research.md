# sources/distributed-fs/xrootd/src/XrdOssCsi/XrdOssCsiFile.cc

Purpose: implements the per-open checksum-enforcing file wrapper. It opens the data file and associated tag file, verifies reads, updates/stores checksums on writes, and keeps shared per-tag `XrdOssCsiPages` state consistent across concurrent opens.

Important APIs/functions: `pageAndFileOpen()` takes/locks the map item, opens the successor data file, and creates shared pages. `createPageUpdater()` opens or creates the tag file and wraps it with `XrdOssCsiTagstoreFile`/`XrdOssCsiPages`. `Read`, `ReadRaw`, and `ReadV` lock ranges, read data, then call `VerifyRange()`. `Write` and `WriteV` update page metadata before writing data and resync sizes on failures. `pgRead` fetches checksum vectors; `pgWrite` validates optional checksum vectors, stores them, and writes data. `Ftruncate`, `Fstat`, `Fsync`, `Flush`, and `VerificationStatus` delegate through page state.

State/control: `pumap_` maps tag paths to refcounted shared map items. `Close()` waits for AIO completion, closes page map state when last holder releases, then closes the successor. Page range locks are acquired before data operations to serialize checksum metadata and data visibility.

Risks/test signals: write metadata is updated before underlying data writes, so failure paths rely on `resyncSizes()` and range release; zero/short writes could loop if successor returns 0 during write; open with truncate while pages exist returns `-EDEADLK`; compressed files are rejected. Tests should cover aligned/unaligned reads and writes, failure injection for writes/tag opens, concurrent opens, readonly tag fallback, missing tags policy, truncation, and pgRead/pgWrite checksum modes.
