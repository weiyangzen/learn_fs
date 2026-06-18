# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sa.c

This file implements ZFS System Attributes (SA): a generic per-objset mechanism for storing typed attributes in dnode bonus buffers and, when needed, spill blocks. It manages persistent attribute registration, compact layout tables, in-memory lookup indexes, byteswapping, handle lifetime, and the public lookup/update/remove APIs used by ZPL and other DMU consumers.

Core responsibilities:
- Defines the SA storage model where attributes are packed into a bonus buffer and optionally moved into a spill block when the bonus area cannot contain both data and the spill block pointer.
- Maintains per-objset `sa_os_t` state attached to `objset_t`, including attribute registration tables, layout AVL trees by number and hash, cached index tables, update callback, and master ZAP object IDs.
- Supports legacy ZPL objects through fixed `sa_legacy_attrs` and `sa_legacy_zpl_layout`, allowing old `DMU_OT_ZNODE` bonus formats to coexist with newer `DMU_OT_SA` layouts.
- Registers and reconstructs persistent attribute metadata from ZAP objects (`SA_REGISTRY`, `SA_LAYOUTS`) in `sa_setup()`, and tears it all down in `sa_tear_down()`.
- Builds compact layouts from ordered attribute lists, assigns persistent layout numbers, and caches layout-index tables that map attribute IDs to offsets and variable-length indexes.
- Handles SA bonus/spill indexing, lazy spill buffer holding, spill resizing, spill removal when no longer needed, and bonus length/bonus type updates.
- Provides bulk and single-attribute lookup/update/remove APIs: `sa_lookup()`, `sa_bulk_lookup()`, `sa_update()`, `sa_bulk_update()`, `sa_update_from_cb()`, `sa_remove()`, `sa_size()`, and template replacement helpers.
- Performs SA byteswapping on first access when on-disk SA data is from the opposite endian order, using registered byteswap functions for each attribute.
- Provides handle lifecycle APIs over DMU bonus buffers, including shared handle lookup/installation through dbuf user data and destruction that releases index table holds and dbuf holds.
- Includes kernel-only ZPL upgrade helper `sa_add_projid()` to rewrite old objects with a project ID attribute at a layout suitable for quota accounting.

Important control-flow notes:
- `sa_setup()` is the objset-level constructor. It creates `sa_os_t`, discovers registry/layout ZAP objects, builds the attribute table from caller registration plus legacy/foreign persisted registrations, loads layout entries, and installs legacy ZPL layouts for filesystem objsets.
- `sa_attr_table_setup()` assigns stable attribute IDs. Legacy ZPL names keep their fixed historical IDs; persisted registry entries keep their encoded IDs; new caller-provided attributes get new IDs and are later persisted by `sa_attr_register_sync()`.
- `sa_attr_op()` is the central lookup/update dispatcher. It checks the bonus index first, lazily opens the spill block if needed, copies data for lookups, updates in-place when size is unchanged, and delegates add/remove/size-changing replacement to `sa_modify_attrs()`.
- `sa_build_layouts()` rewrites the entire packed attribute set. It computes header/data sizes, decides where spill begins, sizes bonus and spill storage, copies attribute data, creates or reuses layout numbers, updates SA headers, rebuilds index tables, and removes an obsolete spill block if all data fits in bonus again.
- `sa_find_sizes()` determines packed data size, header size, variable-length header overhead, and the first attribute that would spill from the bonus buffer.
- `sa_modify_attrs()` snapshots existing bonus/spill bytes, reconstructs a complete attribute descriptor list with one attribute added, removed, or replaced, then calls `sa_build_layouts()` to rewrite both buffers consistently.
- `sa_find_idx_tab()` reuses cached index tables when the layout and variable-length sizes match; otherwise it iterates attributes with `sa_attr_iter()` and builds a new offset table.
- `sa_build_index()` is called when a handle is created or buffers are rewritten. It performs delayed byteswap if needed and attaches the correct index table to the handle for bonus or spill.
- `sa_byteswap()` swaps the SA header, variable-length array, and each attribute payload according to the per-attribute byteswap class. Spill buffers are thawed/re-frozen around mutation.
- `sa_replace_all_by_template_locked()` registers unregistered attributes if needed, then performs full-layout construction. It is the intended fast path for new object creation or full legacy-to-SA conversion.

Key dependencies:
- DMU/dbuf/dnode APIs for bonus holds, spill holds, dirty marking, bonus sizing, bonus type conversion, spill block sizing/removal, object info, and object size.
- ZAP APIs for persistent attribute registry and layout tables.
- AVL trees and lists for layout lookup/caching, plus ZFS refcounts for index table lifetime.
- ARC buffer freeze/thaw/release behavior for safely byteswapping spill buffers.
- ZPL/znode/ACL code under `_KERNEL` for legacy object conversion and project quota layout upgrades.

Risk-sensitive invariants:
- Layout numbers and attribute IDs are persistent on-disk metadata; legacy ZPL layout number 0 and dummy empty layout 1 have special meaning.
- Attribute payloads are 8-byte aligned while packed, and header size must match the number of variable-length attributes in the selected layout.
- Duplicate attributes are not allowed in a layout; adding, removing, or changing the length of a variable-size attribute rewrites the whole attribute set.
- Spill placement must preserve room for the spill block pointer in the bonus buffer.
- `sa_handle_t` index table holds must be released exactly once on handle destruction or rebuild.
- Byteswapping depends on the objset SA registry and layout table being available; SA data is not self-describing enough for generic ZFS byteswap handling.
- `sa_add_projid()` must coordinate znode locks, cached ACL state, and object bonus type conversion so project quota accounting can use fixed expected offsets after upgrade.
