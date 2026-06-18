## sources/user-network-fs/blobfuse2/internal/base_component.go

Purpose: Provides default forwarding implementations for the `Component` interface so components can embed `BaseComponent` and override only relevant operations.

Important APIs and flow: Holds component name and next component. Pipeline methods expose name, config, priority, next linkage, start, and stop. Directory, file, symlink, filesystem, block, and stat methods check `base.next` and forward to it, otherwise return neutral zero values. `SetNextComponent` panics if called more than once.

State and dependencies: State is the next-component pointer and component name. It depends on all internal option structs, `handlemap.Handle`, `common.BlockOffsetList`, and `syscall.Statfs_t`.

Integration points: Every concrete component can embed this to participate in a chain. Xload and loopback both use internal component conventions; libfuse calls into the top component and expects errors/attributes to propagate.

Risks: Neutral nil success defaults can hide missing implementations when no next component exists. Single-assignment next pointer prevents dynamic rewiring. No direct tests here; behavior is exercised by xload `XBase` tests separately and by components embedding `BaseComponent`.
