# sources/storage-engines/pebble/internal/manifest/annotator_blob.go

## Purpose
This file adapts the generic B-tree annotator to `BlobFileSet`, allowing callers to compute aggregate values over all blob files in a version using cached B-tree subtree annotations.

## Important APIs, Types, And Functions
`BlobFileAnnotator[T]` embeds `annotator[T, BlobFileMetadata]`. `MakeBlobFileAnnotator` builds an annotator from a `BlobFileAnnotationIdx` and `BlobFileAnnotatorFuncs`. `BlobFileAnnotatorFuncs` supplies `Merge` and `BlobFile` callbacks. `Annotation` computes the aggregate over a `BlobFileSet`. `BlobFileAnnotationIdx` and `NewBlobAnnotationIdx` provide globally unique cache slots for blob annotations.

## Control Flow
Construction wraps caller-supplied callbacks into the generic `annotator`. `Annotation` returns a zero `T` for an empty blob file set; otherwise it calls `nodeAnnotation` on the set's B-tree root and returns the computed value. `NewBlobAnnotationIdx` increments a package-global counter and panics with an assertion failure if more than `maxAnnotationsPerNode` blob annotators are allocated.

## State, Persistence, And Side Effects
Annotator indexes are process-global initialization state. Computed values are cached in B-tree nodes within `BlobFileSet` and invalidated when nodes mutate. No annotation data is persisted to the manifest; it is derived from manifest-backed blob metadata.

## Dependencies And Integration Points
The file depends on CockroachDB `errors` for assertion panics. It integrates with `BlobFileSet`, the generic B-tree, and blob-file metadata management in `blob_metadata.go`. The design mirrors table annotation in `annotator_table.go`.

## Risks And Edge Cases
The global index allocator is not synchronized and is intended for global initialization, not dynamic concurrent allocation. Exceeding four annotation slots panics. Callback correctness is critical: unstable blob-file properties must return `cacheOK=false`, and merge must be associative enough for tree-shaped aggregation to match linear aggregation.

## Test Signals
There is no direct blob annotator test in this subset. Confidence comes from the shared generic annotator tests and from `BlobFileSet` B-tree tests. Consumers adding blob annotators should add focused tests for cacheability and aggregate correctness.
