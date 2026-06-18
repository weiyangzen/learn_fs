# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsKey.hh

Purpose: declares the key, location, and item structures used by the CMS namespace-location cache.

Important APIs/types/functions: `XrdCmsKey` stores path value, length, CRC hash, tick/ref fields, and equivalence operators. `XrdCmsKeyLoc` stores server masks for have/pending/query, server currency, nil-entry lifetime, saved hash/deadline, and pending redirect counts. `XrdCmsKeyItem` combines a key and location with hash/freelist links and exposes pooled allocation, reload, unload, recycle, replenish, and stats.

Control flow: the header defines fast inline equality by hash/path and approximate equivalence by hash/ref. `XrdCmsKeyItem` lifecycle is allocate from pool, insert into cache/hash, unload from tick tracking, recycle back to free list.

State and persistence behavior: cache entries are transient in memory. `hfvec`, `pfvec`, and `qfvec` persist file-location knowledge within the running cmsd. `lifeline` and `deadline` encode time-based validity, not durable state.

Dependencies: `XrdCmsTypes.hh` for `SMask_t`, C string helpers.

Integration points: used by `XrdCmsCache`, `XrdCmsNash`, cluster selection, state query dispatch, and redirect wait queues.

Risks: manual memory ownership of `Val` is subtle: constructors can wrap non-owned input, but assignment duplicates. No destructor frees `Val`; recycling does. Inline `Equiv()` ignores `Val` and relies on hash/ref uniqueness. No built-in locking.

Test signals: copy/equality behavior, location assignment preserving masks/counters, item pool lifecycle, and cache-level tests for stale key invalidation.
