# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsNash.hh

Purpose: declares `XrdCmsNash`, the non-shrinking hash table for CMS cache key items.

Important APIs/types/functions: `Add(XrdCmsKey&)`, `Find(XrdCmsKey&)`, `Recycle(XrdCmsKeyItem*)`, constructor with previous/current Fibonacci sizes, private `Expand()`, table pointer, sizes, item count, and expansion threshold.

Control flow: the public API supports insert, lookup, and removal/recycle. Expansion is internal and based on `LoadMax`.

State and persistence behavior: owns the hash bucket array and count/threshold metadata for daemon lifetime. It does not own durable state.

Dependencies: `XrdCmsKey.hh`.

Integration points: embedded in `XrdCmsCache` and paired with `XrdCmsKeyItem` pool/tick unload logic.

Risks: no copy prevention, no locking, and destructor intentionally does nothing because normal usage does not delete the global cache. Constructor comments require caller to pass correct Fibonacci antecedents for desired growth behavior.

Test signals: header compile tests, constructor sizing tests, and integration with key item lifecycle.
