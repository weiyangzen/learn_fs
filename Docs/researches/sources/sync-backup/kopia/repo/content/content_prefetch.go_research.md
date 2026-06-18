# sources/sync-backup/kopia/repo/content/content_prefetch.go

Final split target: `Docs/researches/sources/sync-backup/kopia/repo/content/content_prefetch.go_research.md`.

Purpose: implements cache prefetching for a set of content IDs, choosing between whole-pack blob prefetch and individual content fetches based on a caller hint and how much content is requested from each pack.

Important APIs: `prefetchOptions` stores thresholds for count and bytes. `defaultPrefetchOptions` switches to full-blob prefetch when at least two contents totaling at least 5 MB come from a pack. Hints map as `default` or empty to default, `contents` to individual content, `blobs` to whole blobs, and `none` to only resolve IDs without fetching. `WriteManager.PrefetchContents` returns the subset of IDs that resolved to known content info.

Control flow: under `RLock`, content IDs are resolved to `Info` records and grouped by `PackBlobID`. Unknown IDs are skipped. If hint is `none`, the method returns resolved IDs. Otherwise a work channel emits either pack blob prefetch jobs or content-ID jobs. `parallelFetches` workers call the content or metadata cache depending on pack prefix, or read individual contents through `getContentDataAndInfo`.

State and persistence behavior: prefetch is best-effort cache state only. It logs errors and continues, and does not change repository indexes or content data.

Dependencies: content and metadata caches, pack blob prefixes `p` and `q`, gather buffers, logging, and content lookup.

Risks and tests: the lock is held while workers run, which favors consistent info over write concurrency. Hint thresholds influence cache footprint. `TestPrefetchContent` verifies returned IDs and expected cache keys across hints and pack grouping cases.
