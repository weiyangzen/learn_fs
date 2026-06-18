# sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsConfigCP.hh

## Purpose

This header declares `XrdOfsConfigCP`, the OFS configuration helper for checkpoint recovery support. It is a small static-only class that exposes global checkpoint settings, parses checkpoint-related configuration, initializes the feature, and recovers checkpoint files through an internal stats accumulator.

## Important APIs, types, and functions

The public static state is the main API: `Path` names the checkpoint path, `MaxSZ` and `MaxVZ` bound checkpoint size/count behavior, and `cprErrNA`, `Enabled`, `isProxy`, and `EnForce` advertise policy and runtime mode. `Init()` performs feature initialization, and `Parse(XrdOucStream &Config)` consumes configuration tokens from the shared XRootD config stream.

The private `Stats` struct tracks recovery totals: files seen, recovered, errored, skipped, and unresolved. `Recover(const char *ckpPath, Stats &stats)` is private because callers use `Init()`/`Parse()` rather than invoking recovery directly.

## Control flow

The intended flow is configuration parse, initialization, then optional recovery. `Parse()` reads the directive body from `XrdOucStream` and updates the static fields. `Init()` checks those fields and arranges recovery or runtime enablement. `Recover()` walks the checkpoint path and updates `Stats`, with logging and final reporting expected in the implementation file outside this work item.

## State and persistence behavior

All configuration is process-global static state. The header itself owns no durable data, but it points at durable checkpoint files on disk through `Path`. Recovery mutates filesystem state indirectly by reading checkpoint records and resolving pending operations.

## Dependencies and integration points

The only direct type dependency is `XrdOucStream`; the class integrates with the larger OFS configuration parser and with checkpoint/recovery code implemented in `XrdOfsConfigCP.cc`. `isProxy` suggests behavior is sensitive to proxy mode, while `EnForce` and `cprErrNA` likely affect how strictly checkpoint failures are handled.

## Risks and test signals

The main risk is global mutable state: multiple parses or partial initialization can leave stale path or limit values. Recovery must be careful with malformed checkpoint files, missing paths, and proxy deployments. Useful tests should cover disabled configuration, invalid limits, missing checkpoint paths, recovery stats accounting, and idempotence when `Init()` is called more than once.
