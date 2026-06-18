# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/zfs.h

## Role

Public shared ZFS header for kernel/userland ABI constants, dataset and pool properties, feature/version numbers, pool configuration nvlist keys, vdev/pool states, statistics structures, ioctl numbers, ZFS-specific error codes, encryption/key enums, wait/trim/initialize command keys, and sysevent payload names.

## Dataset and Property ABI

Defines `zfs_type_t`, `dmu_objset_type_t`, dataset name/value length limits, `zfs_prop_t`, `zfs_userquota_prop_t`, `zpool_prop_t`, property source flags, received-property markers, rootfs property nvlist key, and property helper function prototypes shared with libzfs/kernel. Property enum comments require appending new values and updating the relevant property tables.

## Feature and Version Constants

Defines SPA versions 1 through 28 and feature-flag version 5000, current `SPA_VERSION`, support predicate, symbolic version feature names, ZPL versions 1 through 5, persistent L2ARC version, PBKDF2 iteration defaults/minimums, and rewind policy flags plus `zpool_load_policy_t`.

## Pool and Vdev Configuration

Declares a large set of nvlist key strings for pool configs, vdev trees, stats, queues, histograms, spares, L2ARC, holes, DDT, split pools, device removal, resilver, comments, checkpoint/load/import state, unsupported features, vdev ZAPs, trim/initialize state, MMP, and allocation bias. Defines vdev type strings and allocation-bias values.

## State and Statistics Types

Defines vdev state and aux-state enums, pool state, MMP state, scan/scrub/initialize/trim command enums, ZIO types, `pool_scan_stat_t`, errata enum, removal/checkpoint stats, scan/checkpoint states, vdev initialize/trim states, fixed-layout `vdev_stat_t`, extended `vdev_stat_ex_t` with queue and histogram arrays, DDT object/stat/histogram types, and histogram bucket helpers.

## Device and Ioctl ABI

Defines driver names and device paths for `/dev/zfs`, zvol, disk roots, and zvol blocksize. `zfs_ioc_t` enumerates `/dev/zfs` ioctl command numbers for pool, vdev, object set, dataset, property, send/receive, fault injection, ACL, sharing, userspace accounting, holds, split, diff, clone/bookmark, sync, channel programs, encryption key management, remap, checkpoint, initialize, trim, redaction, bookmark props, wait, and platform-specific event/bootenv/jail commands.

## Errors, Encryption, Events

Defines ZFS-specific errno values starting at 1024, SPA load states, `zio_encrypt`, pool wait activities, error-list key names, history-log nvlist names, initialize/trim/wait argument keys, online/offline/import flags, channel program keys and limits, and sysevent payload names.

## Risk Notes

This is broad public ABI. Enum ordering, ioctl numbering, fixed-size statistics arrays, and nvlist key strings must remain stable. The comment for `ZIO_PRIORITY_N_QUEUEABLE` requires synchronization with kernel `ZIO_PRIORITY_NUM_QUEUEABLE`.
