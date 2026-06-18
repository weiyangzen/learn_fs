# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsRTable.cc

Purpose: implements the redirector table, a process-wide slot map from short redirector numbers to `XrdCmsNode` objects.

Important APIs/functions: global `XrdCms::RTable`; `Add()` finds a free slot from 1 to `maxRD-1`, updates high-water mark, and returns the slot; `Del()` removes a node and shrinks high-water mark; `Find()` validates slot and node instance; `Send()` broadcasts a message to all redirectors.

Control flow: `Add`, `Del`, and `Send` take the internal mutex. `Find()` intentionally does not lock; callers must hold `Lock()`/`UnLock()` around find plus node use to prevent deletion races.

State and persistence: `Rtable[maxRD]` stores raw node pointers and `Hwm` tracks scan range. No persistent state.

Dependencies/integration: depends on `XrdCmsNode`, CMS mask constants, and trace logging. Used by `XrdCmsProtocol::Admit_Redirector`, `XrdCmsRRQ` fast responses, and `XrdCmsState` status broadcasts.

Risks: manual locking contract for `Find()` is easy to violate. Slot exhaustion returns 0 and rejects redirector login. Raw pointers require redirector deletion to remove the table entry first.

Test signals: add/delete/hwm edge cases, slot reuse, instance mismatch on stale slot, and lock-order checks with RRQ/state send paths.
