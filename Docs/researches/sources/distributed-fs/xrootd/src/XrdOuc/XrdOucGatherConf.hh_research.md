# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucGatherConf.hh

## Purpose
Declares `XrdOucGatherConf`, a utility for collecting selected configuration directives and then tokenizing the gathered subset.

## Important APIs, Types, And Functions
The `Level` enum controls gathered output: `full_lines`, `trim_lines`, `only_body`, and `trim_body`. Public API includes `Gather`, `GetLine`, `GetToken`, `LastLine`, `hasData`, `MsgE`, `MsgW`, `MsgfE`, `MsgfW`, `RetToken`, `Tabs`, `useData`, `EchoLine`, and `EchoOrder`. Constructors accept either a space-separated wanted string or null-terminated vector.

## Control Flow
Callers construct with desired directive names/prefixes, call `Gather` or `useData`, then iterate lines and tokens. Diagnostic helpers include the last consumed line to improve config error messages.

## State And Persistence
Hides all mutable state behind `XrdOucGatherConfData *gcP`. The object owns gathered data and match-list allocations until destruction.

## Dependencies And Integration Points
Forward-declares `XrdSysError` and `XrdOucGatherConfData`. It is a parser helper for plugin and subsystem configuration code.

## Risks And Test Signals
Risks are declaration/implementation mismatch, exceptions from message methods without `XrdSysError`, and callers retaining pointers returned by tokenizer after new gather/destruction. Test signals are API-level parse loops and message helpers for each `Level`.
