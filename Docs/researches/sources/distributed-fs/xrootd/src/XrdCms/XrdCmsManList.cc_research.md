# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsManList.cc

Purpose: implements a thread-safe alternate-manager list used when managers redirect nodes to other managers or supervisor levels.

Important APIs/types/functions: local `XrdCmsManRef`, `XrdCmsManList::{Add(netAddr,redList,port,lvl),Add(ref,manager,port,lvl),Del,getRef,Next}`.

Control flow: public `Add()` gets or creates a reference id for the source network address, deletes any previous entries for that ref, tokenizes the redirect list, and adds each target. Private `Add()` parses optional ports, canonicalizes addresses to names, rejects duplicates, and inserts by manager level. `Del()` removes all entries with a reference id and repairs the iteration pointer. `getRef()` formats an address, looks it up in `refList`, or inserts a new negative reference number. `Next()` returns the current manager/port/level and advances the round-robin pointer, resetting to the head when exhausted.

State and persistence behavior: in-memory linked lists only: `refList` maps source addresses to refs, `allMans` stores alternate managers, and `nextMan` is iteration state. Entries own duplicated manager names.

Dependencies: `XrdNetAddr`, `XrdNetAddrInfo`, `XrdOucTList`, `XrdOucTokenizer`, `XrdSysMutex`, and platform string helpers.

Integration points: `XrdCmsManager` owns an `XrdCmsManList` and `XrdCmsNode::do_Try()` adds alternates from redirect hints. Protocol connection code can call `Next()` to attempt alternate managers.

Risks: `refList` is not freed in the destructor, while `allMans` is. `Next()` returns level zero both for no entry and for a root-level manager, so callers need buffer/port side effects to distinguish if necessary. `Add()` mutates the token buffer temporarily when parsing ports. Insertion-by-level logic is fragile around head ordering.

Test signals: duplicate suppression, IPv4/IPv6 host:port parsing, address canonicalization, deletion by ref while iterating, level ordering, round-robin wraparound, and leak checks for ref list ownership.
