<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPfc/XrdPfc.hh -->
# sources/distributed-fs/xrootd/src/XrdPfc/XrdPfc.hh

## Purpose

`XrdPfc.hh` declares the proxy file cache configuration model and the central `XrdPfc::Cache` class that implements the `XrdOucCache` plugin interface.

## Important APIs, Types, And Functions

- `MutexHolder` is a small RAII locker for XRootD-style mutexes.
- `Configuration` stores all cache tunables: write-through, HDFS mode, command URLs, spaces, disk/file watermarks, purge intervals, directory stats, block size, RAM, write queue, prefetch, checksum policy, only-if-cached thresholds, HTTP cache-control, and QFS redirection.
- `TmpConfiguration` stores raw config strings that require OSS capacity before conversion.
- `Cache` inherits `XrdOucCache` and declares overrides for `Attach`, `LocalFilePath`, `Prepare`, `Stat`, `Unlink`, and `ConsiderCached`.
- The class exposes cache internals needed by file IO, resource monitor, purge, and FSctl code: `GetFile`, `ReleaseFile`, write queue management, RAM management, prefetch registration, active/purge protection, metadata xattr helpers, and command execution.

## Control Flow

The header defines the public contract used by XRootD core and by other XrdPfc components. Configuration is parsed through `Config()` and private directive helpers; runtime IO enters through `Attach()` and related `XrdOucCache` virtual methods. Other PFC classes use `GetInstance()`/`Conf()` to access process-global cache state.

## State And Persistence

The declaration shows major mutable state: singleton `m_instance`, scheduler pointer, environment/logger/trace, OSS instance, g-stream pointer, resource monitor, plugin vectors, purge pin, configuration, prefetch condition/list, RAM accounting, active map, purge-delay set, and write queue. Persistent effects happen through the OSS and metadata helpers declared here.

## Dependencies And Integration Points

It depends on XRootD scheduler, threading, cache, callback, URL, PFC file, and decision headers. It is included by most XrdPfc implementation files and by code that needs cache plugin types.

## Risks And Edge Cases

- The singleton design assumes one cache instance per process.
- Many shared structures are manually protected by `XrdSysCondVar`/`XrdSysMutex`; correct lock ownership is a cross-file contract.
- Private config parser helpers are exposed only through the header, so test code may need friend-like access or integration tests.
- `Configuration::is_purge_plugin_set_up()` currently always returns false despite `m_purge_pin` support in `Cache`.

## Test Signals

Compile tests should ensure external consumers can include installed headers. Runtime tests should validate default `Configuration` values, checksum helper predicates, singleton lifecycle, cache virtual method dispatch, and thread-safety assumptions around active map and write queue via integration tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPfc/XrdPfc.hh -->
