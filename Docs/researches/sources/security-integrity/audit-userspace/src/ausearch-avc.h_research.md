## sources/security-integrity/audit-userspace/src/ausearch-avc.h

Purpose: defines AVC parsing/storage types used across `ausearch` and `aureport`.

Important APIs/types: `avc_t` has `AVC_UNSET`, `AVC_DENIED`, and `AVC_GRANTED`. `anode` stores `scontext`, `tcontext`, result, permission, class, and next pointer. `alist` stores head/current and count. The header exposes creation, append, clear, initialization, and filtered subject/object/result iteration.

Control flow/state: an `alist` usually hangs off `search_items.avc` inside an `llist`; parsers fill it lazily only when subject/object/context filters or reports need it.

Dependencies/integration: includes `libaudit.h` and is included by `ausearch-llist.h`, making these structures part of the shared event model.

Risks/test signals: comments still mention the string module, but the ABI is AVC-specific. Because `alist_first()` and `alist_get_cur()` are inline cursor helpers, callers must account for destructive cursor movement. Tests should verify that callers can perform repeated subject/object scans by resetting the cursor.
