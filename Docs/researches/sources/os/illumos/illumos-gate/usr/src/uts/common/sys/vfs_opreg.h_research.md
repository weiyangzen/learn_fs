# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/vfs_opreg.h

## Role

`vfs_opreg.h` defines the generic operation-registration mechanism used to construct VFS, vnode, FEM, and FSEM operation vectors from named operation-definition tables.

## Key Interfaces

The central type is `fs_func_p`, a union that includes:
- a generic function pointer,
- an error-function pointer,
- all `VFS_OPS`,
- all `VNODE_OPS`,
- all `FEM_OPS`,
- all `FSEM_OPS`.

This lets filesystem code use C99 designated initializers with strong type checking when filling `fs_operation_def_t` arrays.

`fs_operation_def_t` maps an operation name to an implementation function. `fs_operation_trans_def_t` is the master-table entry used by the registration layer: operation name, byte offset in the destination vector, default function, and error function.

## Integration Points

The header exposes:
- `fs_default()` and `fs_error()` placeholders.
- `fs_build_vector()` for constructing an operation vector from a translation table and implementation table.
- `vn_make_ops()` and `vn_freevnodeops()` for vnode operations.
- `vfs_setfsops()`, `vfs_makefsops()`, `vfs_freevfsops()`, and `vfs_freevfsops_by_type()` for VFS operation vectors.

## Research Notes

This header is kernel-only and depends on `vfs.h` and `fem.h`. It is the bridge between string-named operation tables used by filesystem modules and the concrete function-pointer vectors consumed by generic VFS/VOP dispatch.
