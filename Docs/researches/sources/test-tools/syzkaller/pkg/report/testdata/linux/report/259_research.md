<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/259 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/259

## Purpose
This fixture verifies warning parsing for a kmalloc-size bug reached through extended attribute retrieval. The expected title is `WARNING: kmalloc bug in vfs_getxattr_alloc`, type `WARNING`, and `PANICKED: Y`.

## Important APIs, Types, and Functions
The raw log starts at `WARNING: CPU... mm/slab_common.c:1031 kmalloc_slab` and immediately includes `panic_on_warn set`. Parser pieces include warning extraction, panic-on-warn handling, and selecting a meaningful non-helper frame. Key symbols include `kmalloc_slab`, `panic`, `__warn.cold.8`, `do_invalid_op`, `vfs_getxattr_alloc`, `__kmalloc_track_caller`, `krealloc`, `cap_inode_getsecurity`, and `security_inode_getsecurity`.

## Control Flow
The reporter encounters a warning in allocation internals, then walks the stack past warn/panic helpers and allocation helpers to title the report at `vfs_getxattr_alloc`. User-space register tail lines must remain part of the same report.

## State and Persistence Behavior
The fixture persists expected metadata and a raw warning log. There is no runtime state.

## Dependencies and Integration Points
It depends on Linux warning rules, helper-frame suppression, panic detection, and crash type mapping to `WARNING`.

## Risks and Edge Cases
Allocation helper frames such as `kmalloc_slab`, `__kmalloc_track_caller`, and `krealloc` can obscure the higher-level xattr operation. The panic-on-warn section appears before the useful frame.

## Test Signals
The parser must return `WARNING: kmalloc bug in vfs_getxattr_alloc`, type `WARNING`, and panic flag true.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/259 -->
