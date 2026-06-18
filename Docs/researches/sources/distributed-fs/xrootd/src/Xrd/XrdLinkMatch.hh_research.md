## sources/distributed-fs/xrootd/src/Xrd/XrdLinkMatch.hh

Purpose: declares `XrdLinkMatch`, the lightweight matcher used to select active links by client user and host pattern.

Important APIs/types/functions: public `Set()` parses a target expression, and `Match()` has overloads for host strings with explicit or inferred length. Private fields include `Buff`, `Uname`, `HnameL`, `HnameR`, and their lengths.

Control flow: management code creates the matcher from administrative criteria, then passes it into `XrdLink::Find()` or `XrdLink::getName()` for repeated scans.

State/persistence: all parsed data is stored in-place in `Buff`; pointers are invalidated by a later `Set()` call but remain valid for the object lifetime otherwise.

Dependencies/integration: only depends on C string functions and integrates with `XrdLinkCtl`.

Risks: fixed buffer size constrains pattern length. The class is not synchronized; callers must not call `Set()` while another thread is using `Match()` on the same object.

Test signals: compile users should verify both overloads, reset-to-match-all behavior, and match failures for short usernames or hostnames.
