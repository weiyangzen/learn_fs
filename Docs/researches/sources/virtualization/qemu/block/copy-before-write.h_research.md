# File Research: sources/virtualization/qemu/block/copy-before-write.h

Declares the global-state API for the copy-before-write filter. It includes block internals and block-copy definitions, then exposes `bdrv_cbw_append()` and `bdrv_cbw_drop()`.

`bdrv_cbw_append()` takes source and target nodes, optional filter node name, discard-source behavior, minimum cluster size, an output `BlockCopyState **`, CBW error policy, and error target. `bdrv_cbw_drop()` removes a CBW filter and unreferences it. The header is intentionally small and only exports lifecycle operations.
