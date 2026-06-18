# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zap_impl.h

This private header defines microzap/fatzap physical layouts and internal ZAP locking, naming, hashing, and fatzap operations.

Core definitions:
- `ZAP_MAGIC`, block type constants, microzap entry/name/block limits, and `ZAP_NEED_CD`.
- `mzap_ent_phys_t` stores a microzap value, collision differentiator, padding, and fixed-size name; `mzap_phys_t` stores microzap header and variable chunk array.
- `mzap_ent_t` is the in-memory AVL entry for microzap chunks.
- `zap_phys_t` is the fatzap header with magic, pointer table metadata, free block, leaf/entry counts, salt, normalization flags, and ZAP flags.
- `zap_t` stores dbuf user data, objset/object/dbuf, rwlock, micro/fat mode, normalization flags, salt, and mode-specific state.
- Inline `zap_f_phys()` and `zap_m_phys()` return typed physical pointers from the dbuf.
- `zap_name_t` stores original and normalized key forms, hash, match type, normalization flags, and stack normalization buffer.

Internal API surface:
- Match names, lock/unlock directories, evict dbuf user data, allocate/free normalized names, query hash bits/max collision differentiator/flags.
- Fatzap byteswap, count, lookup/prefetch/add/update/length/remove/cursor/stat operations, leaf release, add-with-collision-differentiator, and micro-to-fat upgrade.

Risk-sensitive invariants:
- Comments explicitly require `zap_byteswap()` updates if `zap_phys_t` changes.
- Embedded pointer-table layout depends on fatzap block shift and begins halfway through the block.
- Locking mode parameters in `zap_lockdir()` control writer/reader and add-specific behavior.
