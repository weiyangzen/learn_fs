# sources/user-network-fs/samba/source3/lib/dmallocmsg.c

Purpose: registers Samba messaging callbacks for optional dmalloc heap diagnostics in live daemons.

Important APIs/types/functions: `register_dmalloc_msgs()`, `msg_req_dmalloc_mark()`, `msg_req_dmalloc_log_changed()`, and static `our_dm_mark` under `ENABLE_DMALLOC`.

Control flow: messaging initialization registers handlers for `MSG_REQ_DMALLOC_MARK` and `MSG_REQ_DMALLOC_LOG_CHANGED`. Supported builds mark the heap then log changes since the mark; unsupported builds only log that dmalloc is unavailable.

State/persistence behavior: process-local mark only; no durable state.

Dependencies/integration: depends on Samba messaging and optional dmalloc symbols. It is wired from `messages.c`.

Risks/test signals: behavior is build-option dependent. Compile coverage in both dmalloc and non-dmalloc builds plus message registration smoke tests are the useful signals.
