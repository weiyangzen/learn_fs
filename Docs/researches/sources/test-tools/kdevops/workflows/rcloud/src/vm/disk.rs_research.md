<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/rcloud/src/vm/disk.rs -->
# sources/test-tools/kdevops/workflows/rcloud/src/vm/disk.rs

## Purpose
This module provides disk helpers for rcloud VM creation and deletion.

## Important APIs and Functions
`create_cow_disk(base_image, target_disk, size_gb)` creates parent directories and invokes `qemu-img create -f qcow2 -b <base> -F raw <target> <size>G`. `delete_disk(disk_path)` removes a disk file if it exists. `get_vm_disk_dir(storage_pool, vm_name)` returns `<storage_pool>/<vm_name>`. `get_root_disk_path(storage_pool, vm_name)` returns `<storage_pool>/<vm_name>/root.qcow2`.

## Control Flow
Disk creation logs intent, creates the directory, runs `qemu-img`, checks the exit status, and bails with stderr on failure. Deletion is idempotent for missing files.

## State, Persistence, and Dependencies
Persistent state is VM disk directories and qcow2 root disks under the configured storage pool. The module depends on filesystem access, `qemu-img`, and assumptions that base images are raw format.

## Risks and Test Signals
The backing format is hard-coded as raw even though filenames may vary. VM names directly shape filesystem paths, so name validation is needed upstream to avoid path traversal or collisions. Tests should cover path helpers, failed `qemu-img`, existing directories, and cleanup after partial creation.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/rcloud/src/vm/disk.rs -->
