# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_PSEUDO/pseudofs_methods.h

## Purpose
Defines PSEUDO FSAL shared types, supported attributes, object-handle layout, and method prototypes.

## Important APIs, Types, and Functions
Defines `PSEUDO_SUPPORTED_ATTRS`, `pseudo_fsal_module`, `pseudofs_fsal_export`, `pseudo_fsal_obj_handle`, `pseudofs_unopenable_type`, and prototypes for lookup/create-handle/handle-ops/export creation.

## Control Flow
Module, export, and handle files use this shared layout to allocate exports, build in-memory directory nodes, and wire operation vectors.

## State and Persistence Behavior
Describes process-local state only: root handle, export path, child AVL trees, attributes, parent links, indexes, and liveness.

## Dependencies and Integration Points
Includes AVL and list helpers and is consumed by all PSEUDO sources.

## Risks
Many mutable handle fields are shared directly across files, so lock discipline is external. The opaque handle pointer depends on allocation layout after the struct.

## Test Signals
Compile consistency and runtime mkdir/lookup/readdir/unlink plus handle round trips.
