# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsManList.hh

Purpose: declares the alternate manager list abstraction that stores redirect-derived manager endpoints and returns them one at a time.

Important APIs/types/functions: `Add()`, `Del()`, `getRef()`, `haveAlts()`, `Next()`, constructor/destructor, and private `XrdCmsManRef` linked-list state guarded by separate ref and manager-list mutexes.

Control flow: callers add all redirect targets for a source address, delete by source, and iterate with `Next()` until it returns no manager; the next call restarts at the list head.

State and persistence behavior: process-local manager endpoint cache only. `refList` tracks which source address created which manager entries; `allMans` and `nextMan` hold manager list and cursor.

Dependencies: `XrdSysPthread`, `XrdNetAddr`, `XrdOucTList`, and private implementation class `XrdCmsManRef`.

Integration points: manager reconfiguration and try/redirect processing use this list to discover alternative manager routes.

Risks: raw `char *` endpoint input is parsed in implementation. Thread safety is per-method, not per-iteration transaction. The class is linked-list based and not copy-protected.

Test signals: API compile tests, concurrent add/delete/next stress, and redirect workflow tests from node try handling.
