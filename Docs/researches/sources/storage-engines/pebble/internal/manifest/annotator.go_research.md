# sources/storage-engines/pebble/internal/manifest/annotator.go

## Purpose
This file implements the generic annotation cache used over Pebble manifest B-tree nodes. An annotator computes an aggregate value across a subtree of file metadata and caches that aggregate on the node when every contributing item reports that the value is stable.

## Important APIs, Types, And Functions
`annotator[T, M fileMetadata]` holds an annotation index, a merge function, and an item function. `annotationIdx` selects a slot in `nodeAnnotations.cachedValues`. `nodeAnnotations` stores up to `maxAnnotationsPerNode` `atomic.Value` entries per B-tree node. `Reset` clears all cached values when a node is about to mutate. `nodeAnnotation` recursively computes or returns a cached subtree aggregate.

## Control Flow
`nodeAnnotation` first checks the node's cached value for the annotator index. On a cache miss, it allocates a `T`, aggregates every item in the node, recurses into children if the node is internal, and tracks whether all item/subtree annotations were cacheable. It stores the computed pointer only if all contributors were stable. If any item is unstable, the result is returned but not cached, forcing future recomputation.

## State, Persistence, And Side Effects
Annotation state is in-memory only and attached to B-tree nodes. It is not persisted to manifests. Cache invalidation is coupled to B-tree copy-on-write mutation through `nodeAnnotations.Reset` in `mut`. Cached values are stored as pointers in `atomic.Value`, allowing concurrent readers to race benignly to compute and store equivalent results.

## Dependencies And Integration Points
The file depends only on `sync/atomic` plus manifest-local B-tree types. It is the generic substrate for `TableAnnotator` and `BlobFileAnnotator`. It relies on the `fileMetadata` abstraction implemented by `TableMetadata` and `BlobFileMetadata`.

## Risks And Edge Cases
Annotation indexes are global per annotator family and limited by `maxAnnotationsPerNode`. Reusing the same index for incompatible annotators on the same tree can return incorrect cached values. Merge functions must treat the zero value as identity and must be deterministic. Item functions must accurately report cacheability; returning true for mutable statistics would make stale node annotations possible.

## Test Signals
The direct behavior is exercised through `annotator_test.go`, which defines a count annotator and a pick-file annotator, validates level and range annotations, and benchmarks cached aggregation. Blob annotator behavior is structurally similar but not directly tested in this subset.
