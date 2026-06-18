# File Research: sources/os/plan9/plan9/sys/src/cmd/page/cache.c

Provides the page image cache for the `page` viewer. It keeps five cached `(Document*, page, angle)` image entries and moves hits to the front.

`cachedpage` validates page bounds, calls the document’s `drawpage`, normalizes non-zero image origins, applies rotation, and returns a cached `Image`. Failed page rendering in forward-only mode exits; otherwise it returns a small question-mark placeholder.

The cache includes simple sequential readahead. When the viewed page advances or retreats by one, it forks a shared-memory process to render the likely next page while holding the display lock.

`cacheflush` frees cached images and clears document associations; it is also used as a recovery path when allocation fails.
