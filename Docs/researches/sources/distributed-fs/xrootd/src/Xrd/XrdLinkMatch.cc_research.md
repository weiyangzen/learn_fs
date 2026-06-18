## sources/distributed-fs/xrootd/src/Xrd/XrdLinkMatch.cc

Purpose: implements parsing and matching for user/host target patterns used when scanning or terminating links.

Important APIs/types/functions: `Set(target)` parses target strings of the form `[user][*][@[host-prefix][*][host-suffix]]` into buffer-backed user and host components. `Match(uname, unlen, hname, hnlen)` checks optional username prefix, exact host, host prefix, and host suffix matches.

Control flow: callers construct or reset an `XrdLinkMatch`, then `XrdLinkCtl::Find()` and `getName()` call `Match()` for each active link's `ID` and `HostName`. A null, empty, or `"*"` target clears all filters and matches everything.

State/persistence: parsed target state is held in an internal fixed `Buff[256]` plus pointers into that buffer. There is no allocation and no durable persistence.

Dependencies/integration: uses `XrdSysPlatform` for `strlcpy` portability and is consumed by link control scans.

Risks: suffix parsing and suffix matching look suspicious: after replacing `*` with `'\0'`, `Set()` calls `strlen(theast)`, which will always be zero; `Match()` compares the host suffix pointer to `hname` rather than to `HnameR`. These paths should be tested before relying on suffix wildcards. `strlcpy(Buff, target, sizeof(Buff)-1)` leaves one byte unused and silently truncates long targets.

Test signals: unit cases should cover `*`, user-only, `user*`, host exact, `user@host`, `@prefix*`, `@*suffix`, and combined prefix/suffix patterns, including long target truncation.
