# sources/distributed-fs/xrootd/src/XrdBwm/XrdBwmHandle.cc

Purpose: manages lifecycle of BWM request handles, including scheduling, async dispatch, cancellation, completion logging, and handle reuse.

Important APIs/types/functions: static `XrdBwmHandle::Policy`, `Logger`, `Free`, `numQueued`; local `XrdBwmHandleCB` callback/error object pool; `Activate`, public/private `Alloc`, `Dispatch`, `refHandle`, `Retire`, and `setPolicy`.

Control flow: `Activate` calls `Policy->Schedule`. Positive returns immediately dispatch and optionally return visa data; zero fails; negative means queued, so it captures the client callback, installs `myEICB`, records the handle in a hash table, and returns `SFS_STARTED`. `Dispatch` runs in a dedicated thread, blocks on `Policy->Dispatch`, resolves queued handles, waits for callback handoff, marks dispatched/error, and calls the original callback. `Retire` calls `Policy->Done`, removes scheduled refs if needed, emits logger event, frees strings, and returns the object to the pool.

State and persistence: handle objects are pooled in array chunks. Active queued handles are indexed in 256 buckets by policy reference id. Each handle owns duplicated LFN/local/remote strings and timing/counter fields. State is volatile only.

Dependencies and integration points: depends on `XrdBwmPolicy`, `XrdBwmLogger`, XrdSfs async callback/error APIs, XProtocol status codes, and trace macros.

Risks: concurrency is delicate: callback replacement, `myEICB.Wait`, and ref-table removal must remain ordered. `refID % 256` can be negative if custom policies return negative ids incorrectly. Object pooling intentionally never frees arrays. Logger counters `xSize/xTime` are never updated in this file.

Test signals: immediate schedule success, queue then dispatch, queued cancellation before dispatch, dispatch failure, lost handle simulation, logger event fields, and repeated allocation/reuse under concurrency.
