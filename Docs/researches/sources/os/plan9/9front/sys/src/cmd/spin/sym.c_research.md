# File Research: sources/os/plan9/9front/sys/src/cmd/spin/sym.c

`sym.c` implements Spin's main symbol table, scoped name lookup, type tagging, mtype handling, channel-use tracking, and diagnostics for unused variables/channel access.

Key responsibilities:
- Defines global parser symbol state: `context`, ordered symbol list `all_names`, channel ID counter `Nid`, mtype list `Mtype`, and collected `run` statements.
- Provides `hash` and `lookup`, including legacy and newer scope-rule handling through `context`, `owner`, `CurScope`, and `bscp`.
- Applies scope-prefix disambiguation with `disambiguate`.
- Tracks variable-width hints through `trackvar` and `checkrun`.
- Tracks `run` statements and channel parameters through `trackrun`, `trackchanuse`, and `setaccess` calls.
- Assigns primitive types and declaration metadata with `setptype`, including unsigned width checks, visibility flags, channel IDs, and formal-parameter markers.
- Applies `xr`/`xs` channel assertions through `setxus`, `setallxu`, and `setonexu`.
- Registers and resolves mtype values with `setmtype` and `ismtype`.
- Converts type IDs to text with `sputtype`, prints symbols with `symvar`, and dumps all symbols with `symdump`.
- Reports channel access patterns and unused variables with `chanaccess`.

Important interactions:
- `lookup` is called by both lexing and parsing for every identifier-like token.
- `setptype`, `setmtype`, and `setxus` are grammar action targets from `spin.y`.
- `symdump` is used when `dumptab` is requested in `sched`.
- Channel access reports use `Access` lists attached to `Symbol`.

Notable details:
- `hidden` is a bitfield carrying visibility, inferred width, use, formal parameter, and mtype flags.
- Newer scoping accepts a lookup if a stored block scope is a prefix of the current scope, which approximates nested lexical visibility.
