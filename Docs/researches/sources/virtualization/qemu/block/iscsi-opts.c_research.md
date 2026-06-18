# File Research: sources/virtualization/qemu/block/iscsi-opts.c

## Role

`block/iscsi-opts.c` registers static QEMU command-line/configuration options for the iSCSI block driver. It is separate from `iscsi.c` so global `-iscsi` options can be registered when libiscsi support is present.

## Registered Option List

The file defines `qemu_iscsi_opts` with `.name = "iscsi"` and these options:
- `user`: CHAP username.
- `password`: CHAP password.
- `password-secret`: secret object ID containing the CHAP password.
- `header-digest`: HeaderDigest setting, with accepted textual forms listed in help.
- `initiator-name`: initiator IQN name.
- `timeout`: request timeout in seconds, where default `0` means no timeout.

## Initialization

`iscsi_block_opts_init()` calls `qemu_add_opts(&qemu_iscsi_opts)`. The file uses:
- `block_init(iscsi_block_opts_init)` to register at block initialization time.
- `module_opts("iscsi")` to associate the option set with the iSCSI module.

## Relationship to `iscsi.c`

`iscsi.c` later reads these options through `qemu_find_opts("iscsi")` and merges target-specific/default settings into runtime QDict options. This file only declares the user-visible option schema; it does not open connections or implement I/O.
