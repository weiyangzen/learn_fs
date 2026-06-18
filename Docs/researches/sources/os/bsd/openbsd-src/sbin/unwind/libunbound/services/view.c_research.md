# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/services/view.c

`view.c` implements named view storage for Unbound local-zone authority data. A `views` object owns an rbtree of `view` entries plus a tree lock; each `view` owns its name, optional view-specific `local_zones`, optional response-IP set, `isfirst` fallback flag, and its own data lock.

Creation initializes the view tree and lock protection. `view_create()` duplicates the view name, initializes the per-view lock, and marks the non-rbtree fields as protected. `views_enter_view_name()` creates a view, takes the global tree write lock and the new view write lock, inserts it by name, rejects duplicates, and returns the new view still write-locked so configuration can populate it.

`views_apply_cfg()` iterates configured views, rejects a nameless first view, creates each view, records `isfirst`, and builds view-specific local zones when configured. For `isfirst` views, defaults are suppressed because global local zones can be consulted as fallback; configured `local-zones-nodefault` entries are inserted into the local-zone config as `nodefault` zones so they still shape the view-local tree. Ownership of local-zone config lists is transferred to `local_zones_apply_cfg()` and then nulled in the config view.

Lookup and accounting are straightforward. `views_find_view()` searches by name under the global tree read lock, then locks the found view for read or write before releasing the tree lock. `views_get_mem()` sums the container plus every `view_get_mem()` result; `view_get_mem()` includes the name, local zones, and response-IP set. `views_swap_tree()` exchanges rbtree root/count values with a preallocated `views` object for reload-style replacement.

Deletion destroys locks, deletes local-zone and response-IP contents, frees names, traverses the tree postorder for all views, and frees the container. `views_print()` is intentionally a placeholder.
