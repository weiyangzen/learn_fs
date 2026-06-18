# sources/distributed-fs/xrootd/src/XrdFrc/XrdFrcProxy.cc

## Purpose

This file implements `XrdFrcProxy`, the client-facing proxy that maps FRM operations into persistent request queues. It validates request fields, initializes queue agents, supports cancellation, and lists pending work.

## Important APIs, Types, and Functions

The operation-to-queue table maps `getf`, `migr`, `pstg`, and `putf` names to `XrdFrcRequest` queue ids and public operation flags. Public methods are `Add()`, `Del()`, `List(Queues&, char*, int)`, `List(qType, qPrty, Items, Num)`, and `Init()`.

`Init2()` parses the active XRootD configuration for `frm.xfr.qcheck` to discover a queue path, and `qChk()` validates/extracts that path.

## Control Flow

Construction wires logging, enables tracing when requested, derives public and internal instance names, and clears agent pointers. `Init()` determines a queue path from explicit argument, config, or default path, creates queue directories, then starts an `XrdFrcReqAgent` for each requested operation type.

`Add()` maps the request opcode to a queue, checks support, packs `XrdFrcRequest` fields, appends optional opaque data after the LFN with `Opaque` offset, validates URL or absolute path layout, fills user/id/notify/priority/options, and calls the queue agent. `Del()` maps opcode and asks the agent to cancel by request id. `List()` walks queue types and priorities incrementally.

## State and Persistence Behavior

Proxy state is in memory: one agent pointer per queue, instance names, and queue path. Persistent request records are written by `XrdFrcReqAgent`/`XrdFrcReqFile` into queue files. Configuration-derived queue path is copied into `QPath`.

## Dependencies and Integration Points

The implementation depends on `XrdFrcReqAgent`, `XrdFrcUtils`, request types, XrdOuc config streams/utilities, XrdSys logging/platform, and FRM trace facilities. It is a bridge between server/client command handling and on-disk FRM queues.

## Risks and Edge Cases

`Add()` indexes `Agent[qType]` after `MapR2Q()` without an explicit bounds check, relying on utility correctness. Opaque data is packed into `LFN` with embedded NUL separation, so all consumers must honor `Opaque`. `Init2()` only captures the qcheck path if the config directive is present and valid.

## Test Signals

Tests should cover each opcode mapping, unsupported queues, LFN length and URL validation, opaque packing, default user/id/notify values, priority clamping in the agent, config qcheck parsing, and listing across queue types/priorities.
