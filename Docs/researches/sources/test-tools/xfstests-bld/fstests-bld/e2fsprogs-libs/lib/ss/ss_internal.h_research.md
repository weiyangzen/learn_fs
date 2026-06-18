# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/ss/ss_internal.h

## Purpose
`ss_internal.h` defines libss private data structures and internal function prototypes.

## Important APIs, Types, and Functions
Key types include `pointer`, `BOOL`, abbreviation structures, `ss_abbrev_info`, and `ss_data`. Macros include `ss_info()` and `ss_current_request()`. It declares internal helpers for parsing, paging, request listing, command execution, info dirs, and readline completion.

## Control Flow
There is no runtime control flow. It defines the in-memory contract consumed by all ss implementation files.

## State, Persistence, Dependencies, Risks, and Test Signals
State is global `_ss_table`, `_ss_pager_name`, generated `ss_et_msgs`, and per-invocation `ss_data`. Dependencies include `ss.h`, stdio/string/stdlib, and optional signal compatibility macros. Risks include exposing mutable internals across files, unimplemented abbreviation fields, pointer ownership ambiguity, and no synchronization. Test signals are coherent behavior across invocation, parser, listener, pager, and request-table modules.
