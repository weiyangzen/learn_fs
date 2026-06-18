# sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsEvs.hh

## Purpose

This header declares the OFS event sender data model, format table, and sender class used to notify external consumers about filesystem operations.

## Important APIs, types, and functions

`XrdOfsEvsInfo` carries event arguments: trace ID, primary and secondary logical paths, CGI strings, file mode, file size, and optional environment pointers. `XrdOfsEvsFormat` stores a printf-style format, conversion flags, and argument mapping, with `Def()`, `Set()`, and `SNP()` helpers.

`XrdOfsEvs::Event` defines masks and numbered events. `Enabled()` checks an event against the enabled mask, `Notify()` queues an event, `Parse()` overrides a message format, `Start()` launches the sender, `sendEvents()` is the thread loop, and `Prog()` exposes the configured target.

## Control flow

OFS builds an `XrdOfsEvsInfo` for each operation and calls `Notify()` when `Enabled()` returns true. Static `MsgFmt[]` maps each event number to a format. The sender hides destination details behind `Start()` and `sendEvents()`.

## State and persistence behavior

The header defines bounded message sizes and queue limits, but all state lives in memory. `MsgFmt[]` is static and process-wide, so custom parse settings affect all sender instances.

## Dependencies and integration points

It depends on XRootD pthread wrappers and forward-declares environment, program, message, and logger types. It integrates with OFS operation handlers and configuration directives that enable events or override event messages.

## Risks and test signals

The event enum combines bit masks and compact indexes; adding events must update `nCount`, default format initialization, and `eName()`. Static `MsgFmt[]` is mutable global state, so tests should avoid order dependence or reset formats. Header-level tests should check mask composition, small/large message size expectations, and custom format argument ordering.
