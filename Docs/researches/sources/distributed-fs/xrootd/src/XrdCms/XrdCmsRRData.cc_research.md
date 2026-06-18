# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsRRData.cc

Purpose: implements buffer allocation and object pooling for CMS request/response data containers used by protocol dispatch.

Important APIs/functions: `getBuff(size_t)` frees any existing buffer, chooses an alignment based on page size and requested size, uses `posix_memalign`, stores `Buff` and `Blen`, and returns success. `Objectify()` either recycles an object into a static free list or returns an initialized object from that list/new allocation.

Control flow: callers request an object with no argument and return it by passing the pointer back. A static mutex protects the free list. Reused objects reset `Ident` and `Next`, but not every field, so parsers/protocol code must clear relevant fields before use.

State and persistence: static free list is process-local. Each object owns an aligned `Buff` until stolen by `XrdCmsPrepArgs`, replaced by `getBuff()`, or held for reuse. No disk persistence.

Dependencies/integration: uses `sysconf(_SC_PAGESIZE)`, `posix_memalign`, `XrdSysMutex`, and `XrdCmsRRData.hh`. Used heavily by `XrdCmsProtocol::Dispatch()`.

Risks: `getBuff(0)` would request questionable alignment/size behavior; callers currently use positive datalen. The free list never shrinks, so peak request pressure determines retained memory. Partial reset in `Objectify()` can leave stale scalar fields if callers forget to overwrite them.

Test signals: allocation size/alignment tests, repeated recycle tests under thread sanitizer, and parser reuse tests for stale fields.
