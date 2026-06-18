# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucCache.hh

## Purpose
Defines the public cache plugin and cache-I/O abstraction used to interpose local or remote caches in front of XRootD data sources.

## Important APIs and types
`XrdOucCacheIOCB` is the async completion callback with `Done(int)`. `XrdOucCacheIOCD` reports deferred detach completion. `XrdOucCacheOp::Code` defines file/global fcntl-like query operations.

`XrdOucCacheIO` is the per-file source/cache interface. Required methods include `Detach()`, `FSize()`, `Path()`, scalar `Read()`, `Write()`, `Sync()`, and `Trunc()`. Default methods provide unsupported `Fcntl()`, optional `Fstat()`/`Location()`, page read/write wrappers with checksum vectors, synchronous-as-asynchronous callback wrappers, preread hooks, vector I/O, and `Update()` for deferred open replacement. The protected destructor enforces use of `Detach()` rather than direct delete.

`XrdOucCache` is the cache plugin interface. Required `Attach()` wraps an `XrdOucCacheIO`. Optional methods support global fcntl, local-file-path lookup, prepare/defer open, rename/rmdir/stat/truncate/unlink, special `Xeq()`, statistics, and a short `CacheType`. The typedef `XrdOucCache_t` describes the plugin factory signature.

## State, dependencies, and integration
The header depends on cache stats, I/O vectors, range lists, errno, strings, and vectors. It is consumed by cache implementations such as proxy/file caches and by code that loads `XrdOucGetCache` plugins.

## Risks and test signals
The API mixes sync and async paths; default async callbacks may run inline, so callers holding non-recursive locks can deadlock. Ownership and deferred detach are critical. Tests should validate plugin factory loading, attach failure fallback, inline callback behavior, local path return modes, and stats aggregation from deleted cache I/O objects.
