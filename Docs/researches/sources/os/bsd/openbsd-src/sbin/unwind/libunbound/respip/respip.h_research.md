# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/respip/respip.h

Header for the response-IP module.

Defines:
- `struct respip_set`: regional allocator, address rbtree, rw lock, shallow tag-name metadata, and tag count.
- `struct resp_addr`: address-tree node with node lock, tag bitlist, action, and optional local-data rrset.
- `struct respip_client_info`: client tag/action/data attributes and view/view-name context.
- `struct respip_action_info`: selected action, RPZ flags, log name, CNAME override flag, and matched address info pointer.

Declares:
- Set creation/deletion and config application for global and view response-IP data.
- `respip_rewrite_reply()` for applying response-IP/RPZ actions to replies.
- `respip_merge_cname()` for completing redirect CNAME chains.
- Module function block and lifecycle functions.
- Test/introspection helpers for tree access, action lookup, rrset lookup, emptiness, and memory accounting.
- Inform logging helper.
- Address lookup/create/delete and RR insertion helpers.
- `respip_copy_rrset()` and `respip_set_swap_tree()`.

Role:
- Public internal contract between response-IP module, local-zone/tag code, view code, auth-zone/RPZ code, and tests.
- Documents ownership expectations for shallow-copied rrsets and region-allocated rewritten replies.
