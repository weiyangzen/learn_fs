# File Research: sources/virtualization/qemu/block/meson.build

## Role

`block/meson.build` declares the QEMU block subsystem source composition. It decides which block core files, image format drivers, protocol drivers, platform backends, optional modules, generated coroutine wrappers, and subdirectories are included in the build.

## Core Block Sources

The build always adds generated headers and the main block source set including files such as:
- block accounting, backend, copy, jobs, dirty bitmap, graph lock, throttling, mirroring, stream, snapshots,
- core I/O file `io.c`,
- qcow2 implementation files,
- raw format,
- NBD, null, quorum, preallocation, write threshold.

Compression dependencies `zstd` and `zlib` are attached to this core source set.

## Conditional Format and Feature Sources

The file gates optional image formats/features by Meson options:
- `qcow1` adds `qcow.c`,
- `vdi`, `vhdx`, `vmdk`, `vpc`, `cloop`, `bochs`, `vvfat`, `dmg`, `qed`, `parallels`,
- `replication`,
- TCG-only `blkreplay.c`.

Platform-specific local file backends are selected:
- Windows uses `file-win32.c` and `win32-aio.c`.
- Non-Windows uses `file-posix.c` plus `coref` and `iokit`.

Linux-only `nvme.c` is added when `host_os == 'linux'`.

## Optional Protocol/Backend Sources Relevant to This Group

This build file wires the other researched files as follows:
- `iscsi-opts.c` is added to `block_ss` when `libiscsi` is available.
- `iscsi.c` is part of the `block_modules` map when `libiscsi` is found.
- `linux-aio.c` is added when `libaio` is found.
- `io_uring.c` is added when `linux_io_uring` is found.

This means iSCSI driver code may be built as a block module depending on module settings, while the option registration file is part of the block source set when libiscsi exists.

## Module Construction

`block_modules` is a dictionary of optional block protocol modules. The file iterates over:
- blkio,
- curl,
- iscsi,
- nfs,
- ssh,
- rbd.

For each found dependency, it creates a source set and adds the module's source. If `enable_modules` is true, module sources are collected in `modsrc`.

DMG decompression helpers are treated as special block modules:
- `dmg-lzfse`,
- `dmg-bz2`.

## Generated Files

The build defines `module_block.h` using `scripts/modules/module_block.py`, with module source files as input. This generated header is added to `block_ss`.

It also defines `block-gen.c` using `scripts/block-coroutine-wrapper.py`, generated from block I/O headers and `coroutines.h`. This generated C file provides coroutine wrapper plumbing for declared block APIs and is added to the block source set.

## Subdirectories and Final Registration

The build adds `stream.c` after generated wrapper setup, adds `qapi-system.c` to `system_ss`, descends into `export` and `monitor`, and finally appends the `block_modules` dictionary into the global `modules` map under the key `block`.

## Build-System Significance

For this work item, `meson.build` is the linkage map showing how the core I/O layer (`io.c`), Linux async backends (`linux-aio.c`, `io_uring.c`), and iSCSI protocol support (`iscsi-opts.c`, `iscsi.c`) enter QEMU builds based on host platform and detected dependencies.
