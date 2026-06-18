# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucTList.hh

Purpose: defines simple linked-list utility nodes and RAII helpers for text plus small numeric payloads.

Important APIs, types, and functions: `XrdOucTList` stores `next`, duplicated `text`, and a union payload (`dval`, `ival`, `sval`, `cval`, or `val`) with constructors for each payload shape. `XrdOucTListHelper` clears a list anchored by a pointer on destruction. `XrdOucTListFIFO` tracks first/last and supports `Add()`, `Clear()`, and `Pop()`.

Control flow: callers allocate nodes and link them manually or through FIFO `Add()`. Destructors free only the node's own text; list-wide cleanup is performed by helper/FIFO or caller loops.

State and persistence: all state is heap memory owned by the list users. There is no locking or persistence.

Dependencies and integration points: depends on C allocation/string headers. It is used by parsers such as `XrdOucStream` to hold suffix lists and by other utility code needing lightweight text-value lists.

Risks and test signals: `XrdOucTListFIFO::Pop()` returns the full list and clears both FIFO anchors, not a single node. Nodes do not recursively delete `next`, so ownership must be explicit. Tests should cover each constructor, helper cleanup, FIFO add/pop/clear semantics, and null text handling.
