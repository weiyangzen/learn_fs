# sources/user-network-fs/gcsfuse/internal/gcsx/read_manager/read_manager.go

## Scope

This file implements the newer compositional `ReadManager`, which orders multiple `gcsx.Reader` implementations for one object and falls back between them.

## Purpose

`ReadManager` centralizes read orchestration for a file handle. It can prioritize shared chunk cache or traditional file cache, optionally use buffered prefetch reads, and always keep a GCS reader as the final fallback. A shared `ReadTypeClassifier` coordinates read-pattern decisions across those readers.

## Important APIs, Types, And Functions

- `ReadManager` stores object metadata, ordered readers, classifier, and trace handle.
- `ReadManagerConfig` carries cache handlers, MRD wrapper, metrics/tracing, buffered-read knobs, worker pool, semaphore, handle ID, and initial offset.
- `NewReadManager` constructs the reader chain.
- `ReadAt` performs EOF/empty-read handling, sets `req.ReadInfo`, tries readers in order, and records successful reads.
- `CheckInvariants`, `Object`, `ReaderName`, and `Destroy` implement `gcsx.ReadManager`.

## Control Flow

Construction adds one cache reader if configured: shared chunk cache takes precedence over traditional file cache. It then optionally adds a `bufferedread.BufferedReader` if enabled and constructible. Finally it appends `client_readers.GCSReader`. On read, the manager gets current read info, starts a trace span per reader, and advances through the chain only when the reader returns `gcsx.FallbackToAnotherReader`.

## State And Persistence Behavior

The manager itself stores no durable content. It records read pattern state in `ReadTypeClassifier`; cache persistence is handled by cache readers; GCS state is handled by the bucket/client readers. `Destroy` delegates cleanup to every reader in chain order.

## Dependencies And Integration Points

It integrates with `gcsx.FileCacheReader`, `gcsx.SharedChunkCacheReader`, `bufferedread.BufferedReader`, `client_readers.GCSReader`, file cache config, worker pools, semaphores, metrics, tracing, and FUSE handle IDs.

## Risks And Maintenance Notes

Reader order is behaviorally significant. Shared chunk cache and traditional file cache are mutually exclusive in construction; passing both uses shared chunk cache. `config.Config` is dereferenced for buffered-read settings, so callers must provide a non-nil config. Any reader returning a non-fallback error stops the chain, so reader implementations must reserve hard errors for cases that should not fall back. `ReadAt` mutates the request by setting `ReadInfo`; fallback readers depend on `Offset` and `Buffer` remaining unchanged.

## Test Signals

`read_manager_test.go` covers reader-chain construction with file cache, shared absence, buffered read, and buffered creation failure; invalid offsets; GCS errors; clobbered files; full-object cache hit; fallback from first to second reader; and buffered fallback to GCS.
