# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/imap4d/nodes.c

Provides small parser/data-structure helpers for IMAP message sets, fetch lists, store operations, numeric/string lists, and IMAP-safe output formatting.

Key behavior:
- `forMsgs` iterates `MsgSet` ranges by sequence number or UID, applying a callback and accumulating errors.
- `mkStore`, `mkFetch`, `mkNList`, `mkSList` allocate parser nodes from `parseBin`.
- `revFetch`, `revNList`, `revSList` reverse parser-built linked lists.
- `BNList` and `BSList` print numeric and IMAP string lists.
- `Bimapdate` and `Brfc822date` format dates through `imap4date`/`rfc822date`.
- `Bimapstr` emits `NIL`, quoted strings, or IMAP literals depending on content and length.

Integration points:
- Shared by command parser/executor logic for FETCH, STORE, SEARCH, and response formatting.
- Depends on `parseBin`, `parseErr`, `Bprint`, `Bimapstr`, and IMAP data model types from `imap4d.h`.

Risks and notes:
- `forMsgs` treats missing sequence numbers as errors but missing UIDs as ignorable, matching IMAP UID command semantics.
- `Bimapstr` switches to literals for long or unsafe strings, avoiding quote escaping complexity for those cases.
