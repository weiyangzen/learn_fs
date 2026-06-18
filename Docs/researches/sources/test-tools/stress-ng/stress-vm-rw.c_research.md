## sources/test-tools/stress-ng/stress-vm-rw.c

Purpose: Implements `vm-rw`, stressing cross-process memory copying with `process_vm_readv` and `process_vm_writev`.

Important APIs/types/functions: `stress_vm_rw_info`, `stress_vm_child`, `stress_vm_parent`, and `stress_vm_rw`; option `vm-rw-bytes`; uses `clone(CLONE_VM)`, pipes, `process_vm_readv`, `process_vm_writev`, iovecs, and kill/reap helpers.

Control flow: parent computes per-instance transfer size, creates two pipes, clones a child sharing VM, and waits for child buffer-address messages. Parent reads the child buffer in chunks up to 1 GiB, optionally verifies zeros, fills local pages with an incrementing value, probes invalid flags/pids, writes data back to the child, and notifies it. Child verifies the written byte per page when verify is enabled, clears pages, and sends the address again.

State and persistence: transient anonymous mappings, pipes, clone stack, and child pid; no files. Transfer size is page-aligned and split by `iov_count`.

Dependencies/integration: Linux process_vm APIs, `sys/uio.h`, clone support, stress-ng memory usage reporting.

Risks: clone with shared VM plus separate mappings is subtle; pipe termination writes use the wrong pipe descriptor in one cleanup path, but child killing limits impact. Verification is optional.

Test signals: `VERIFY_OPTIONAL`; failures report read/write syscall errors or page-content mismatches, bogo increments after complete read/write cycles.
