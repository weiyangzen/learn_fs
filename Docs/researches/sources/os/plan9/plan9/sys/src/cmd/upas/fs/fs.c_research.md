# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/fs/fs.c

- Role: Implements the `upas/fs` 9P server exposing mailboxes and message parts as a filesystem.
- 9P flow: `main` sets up mailbox state and mounts/posts a pipe; child `io` reads 9P messages, dispatches through `fcalls`, and writes replies.
- Namespace model: Top directory contains `ctl` and mailboxes; mailbox directories contain message directories and optional `ctl`; message directories expose files such as `body`, `header`, `raw`, `from`, `subject`, `info`, `digest`, and MIME fields.
- Key operations: `rattach`, `rwalk`, `ropen`, `rread`, `rwrite`, `rremove`, `rstat`; control writes support `open`, `close`, and `delete`.
- State management: `Fid` tracks qid, mailbox, message, top-level message ref, open state, and directory-read finger pointer; hash table maps parent qid/name to qids and message/mailbox pointers.
- Message handling: `fileinfo`, `readinfo`, `readheader`, `stringconvert`, and RFC2047 helpers prepare content; body opens trigger decode/convert.
- Background sync: Optional reader process polls mailbox qid/version and `waketime`, then calls `syncmbox`.
- Risks/notes: `checkmboxrefs` aborts on reference mismatch, indicating ref-count invariants are critical. `dowalk` temporarily mutates names at dot suffixes for fallback lookup.
