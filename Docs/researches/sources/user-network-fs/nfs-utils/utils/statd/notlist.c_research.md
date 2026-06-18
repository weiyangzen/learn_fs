## sources/user-network-fs/nfs-utils/utils/statd/notlist.c

Purpose: Implements doubly linked-list management for monitored hosts and pending notification/callback work.

Important APIs/types/functions: `nlist_new`, `nlist_insert`, `nlist_insert_timer`, `nlist_remove`, `nlist_clone`, `nlist_free`, `nlist_kill`, and `nlist_gethost`.

Control flow: Entries are allocated with default retry count `MAX_TRIES`; normal insert prepends; timer insert keeps ascending `when`; remove unlinks without freeing; clone copies callback identity and cookie; kill drains the list.

State and persistence: Manages in-memory lists only. Persistent NSM records are handled elsewhere.

Dependencies and integration: Uses `notify_list` macros from `notlist.h`, `xmalloc`, `xstrdup`, and `statd_matchhostname`. Shared by monitor, callback, rmtcall, and service-loop code.

Risks and test signals: Pointer ownership is delicate: `nlist_free` frees inner fields but not the entry itself, while `nlist_kill` frees both. Tests should cover head/middle/tail removal, append timer insertion, clone cookie fields, hostname search, and memory ownership under sanitizers.
