# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdPrepare.hh

## Purpose

This header declares the prepare-log data model and scrub job. `XrdXrootdPrepArgs` carries parsed prepare request data, while `XrdXrootdPrepare` owns the static file-backed prepare tracking interface.

## Important APIs, types, and functions

`XrdXrootdPrepArgs` stores `reqid`, `user`, `notify`, `prty`, `mode`, a linked path list, and private listing state (`DIR *dirP`, cached filter lengths, ownership flags). `XrdXrootdPrepare` exposes `List()`, `Log()`, `Logdel()`, `Open()`, `Scrub()`, and two `setParms()` overloads, plus `DoIt()` for scheduled scrubbing.

## Control flow

Protocol code fills `XrdXrootdPrepArgs` from a `prepare` request. Depending on request mode it logs, lists, opens, or deletes records. The scheduled job calls `Scrub()` periodically and requeues itself using `scrubtime`.

## State and persistence behavior

`XrdXrootdPrepArgs` owns optional heap strings and path lists according to constructor flags; its destructor closes active directory iteration state. `XrdXrootdPrepare` uses static scheduler/logger/log-directory state and stores durable records as files outside the process.

## Dependencies and integration points

The header depends on POSIX `DIR`, `XrdJob`, `XrdScheduler`, `XrdSysError`, and `XrdOucTList`. It is integrated from protocol execution and configuration code for `xrootd.prepare` behavior.

## Risks and edge cases

Ownership flags make `XrdXrootdPrepArgs` flexible but easy to misuse: passing borrowed strings with `freestore=1` or borrowed path nodes with `freepaths=1` will cause invalid frees. `mode` is a four-byte fixed buffer, so parsing must bound writes. The `XrdXrootdPrepare` object is intentionally never deleted.

## Test signals

Signals include destructor ownership behavior, list state cleanup, scheduling after logdir configuration, and correct handling of disabled logging.
