# sources/user-network-fs/samba/source3/libsmb/samlogon_cache.h

Purpose: `samlogon_cache.h` declares the public interface for the Netlogon `netr_SamInfo3` cache implemented in `samlogon_cache.c`. It gives other Samba components a small API for initializing, storing, reading, deleting, existence-checking, and traversing cached logon records.

Important APIs and types: the header forward-declares `struct dom_sid` and `struct netr_SamInfo3` and includes `talloc.h` for ownership contracts. Exported functions are `netsamlogon_cache_init`, `netsamlogon_clear_cached_user`, `netsamlogon_cache_store`, `netsamlogon_cache_get`, `netsamlogon_cache_have`, and `netsamlog_cache_for_all`. The traversal callback receives a SID string, cache timestamp, decoded `netr_SamInfo3`, and caller private data.

Control flow and state: callers normally do not need to call init directly because implementation functions lazily initialize the TDB, but explicit initialization is available. Returned `netr_SamInfo3` values are talloc-owned by the caller-supplied context. Store accepts a mutable `info3` pointer because the implementation may fill missing account/full-name fields before serialization.

Dependencies and integration: this header sits at the boundary between libsmb cache code and consumers in auth/winbind-style code. It depends on SID and Netlogon generated RPC types without including their full definitions, reducing header coupling.

Risks: API consumers must understand that the cache is persistent and security-sensitive, and that stored entries are sanitized by implementation rather than by the header contract. The function name `netsamlog_cache_for_all` omits `on` unlike the other functions, so callers should avoid introducing parallel spellings.

Test signals: compile tests should catch prototype drift. Integration tests should include store/get/delete/traverse behavior through the header rather than only static implementation tests.
