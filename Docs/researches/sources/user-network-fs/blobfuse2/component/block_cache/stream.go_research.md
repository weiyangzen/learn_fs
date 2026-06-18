# sources/user-network-fs/blobfuse2/component/block_cache/stream.go

## Purpose

`stream.go` implements the legacy/config-compatibility `stream` component facade that translates streaming configuration into `block_cache` configuration. It does not perform I/O itself; it maps stream cache knobs into block cache block size, prefetch, and memory size settings.

## Important APIs, Types, and Functions

The file defines `Stream`, `StreamOptions`, constants `compStream` and `mb`, methods `Name` and `Configure`, and an `init` function that registers command-line flags. `StreamOptions` includes `block-size-mb`, `buffer-size-mb`, `max-buffers`, `file-caching`, `read-only`, and v1 compatibility fields `stream-cache-mb` and `max-blocks-per-file`.

## Control Flow

`Configure` unmarshals `stream` config plus global `read-only`. If `max-blocks-per-file` is set, it derives `BufferSize` from block size times max blocks. If `stream-cache-mb` is set with a buffer size, it derives `CachedObjLimit`, clamping to at least one. It checks whether requested memory exceeds `memory.FreeMemory`, logs the final settings, and writes translated values into `block_cache.block-size-mb`, `block_cache.prefetch`, and `block_cache.mem-size-mb`.

## State and Persistence Behavior

The component stores only parsed sizing fields on `Stream`; the significant state mutation is writing into the process-wide config registry before block cache configuration consumes those keys.

## Dependencies and Integration Points

It depends on Blobfuse `config`, `log`, `internal.BaseComponent`, and `pbnjay/memory`. It integrates with `BlockCache` through `config.Set` and with CLI registration through `config.AddFloat64Flag`, `AddIntFlag`, and `AddUint64Flag`.

## Risks and Edge Cases

The memory check multiplies `BufferSize * CachedObjLimit * mb`; overflow or unset values can hide bad config. `FileCaching` and `readOnly` are logged but not otherwise enforced here. This compatibility shim depends on block cache using the translated config keys later in startup.

## Test Signals

`block_cache_test.go` includes `TestZZZZZStreamToBlockCacheConfig`, which sets stream config, enables `common.IsStream`, and checks that block cache receives the expected block size and memory size.
