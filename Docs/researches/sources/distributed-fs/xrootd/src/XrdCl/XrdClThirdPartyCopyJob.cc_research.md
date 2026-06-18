# sources/distributed-fs/xrootd/src/XrdCl/XrdClThirdPartyCopyJob.cc

## Purpose

This file implements XrdCl third-party copy. It validates whether a copy can run remotely, configures destination/source TPC CGI parameters, supports delegated TPC-lite, runs the copy through `File::Sync`, reports progress and cancellation, closes resources, and optionally verifies checksums.

## Important APIs, Types, and Functions

Private helpers include `TPCStatusHandler`, which waits for async sync completion via semaphore; `InitTimeoutCalc`, which tracks remaining initial timeout; and `UpdateErrMsg`, which annotates status messages. Main methods are `Run`, `CanDo`, `RunTPC`, `RunLite`, and `GenerateKey`.

## Control Flow

`Run` calls `CanDo`, dispatches to TPC-lite or vanilla TPC, then performs checksum verification for configured modes. `CanDo` rejects local files and non-root targets, reads job properties (`initTimeout`, checksum settings, `force`, `coerce`, `delegate`), opens the source when possible to resolve actual URL and size, merges original source CGI with redirector CGI, enables or disables delegation, builds destination TPC CGI with `XrdOucTPC::cgiC2Dst`, opens the destination with update/new/delete/force flags, checks destination TPC-lite support, optionally checks source TPC support, and records the remaining init timeout.

`RunTPC` builds source CGI with `cgiC2Src`, syncs the destination rendezvous, opens the source, starts async destination sync, periodically stats the destination for progress, can issue `ofs.tpc cancel`, waits for completion, closes both files, and stores size. `RunLite` follows the destination-only delegated flow. Checksum verification can use preset, metalink redirector checksum, or remote checksum queries and emits monitor checksum events.

## State and Persistence Behavior

State is per-job: destination `File`, resolved `tpcSource`, `realTarget`, rendezvous key, checksum settings, source size, init timeout, copy flags, delegation flag, stream count, and `tpcLite`. Results are persisted only in the provided `PropertyList` keys such as `size`, `sourceCheckSum`, and `targetCheckSum`.

## Dependencies and Integration Points

The implementation integrates copy framework classes, `File`, `URL`, `Utils`, message CGI merging, monitor events, redirector registry/metalink handling, delegated-credential environment, `XrdOucTPC`, semaphores/timers, and XRootD protocol errors.

## Risks and Edge Cases

TPC behavior depends on server capability strings and error normalization. Source open is optional only with delegation; without delegation it becomes fatal. Timeout accounting is subtle because zero has special meaning and close attempts should still happen after expiry. Progress polling every 2.5 seconds can miss fast copies and cancellation waits for async sync completion. `GenerateKey` combines time and process IDs and is not cryptographic. Close failure attribution in `RunTPC` appears to choose the wrong label in the `UpdateErrMsg` argument when source close fails.

## Test Signals

Useful tests include unsupported local/source/target cases, delegated TPC-lite only flow, vanilla rendezvous flow, fallback-triggering `errNotSupported`, cancellation via progress handler, checksum match/mismatch, timeout during `CanDo`, destination open TPC-not-supported mapping, and monitor event emission.
