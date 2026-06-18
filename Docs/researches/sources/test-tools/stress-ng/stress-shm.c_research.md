# sources/test-tools/stress-ng/stress-shm.c

Purpose: implements the POSIX shared memory `shm` stressor, repeatedly creating named `shm_open` objects, sizing, mapping, touching, syncing, changing metadata, unlinking, and checking page contents.

Important APIs/types/functions: `stress_shm`, `stress_shm_posix_child`, `stress_shm_posix_check`, `stress_shm_msg_t`, `shm_open`, `shm_unlink`, `ftruncate`, `mmap`, `munmap`, `msync`, `fstat`, `fchmod`, `fchown`, `shim_fallocate`, `stress_mincore_touch_pages`, `stress_madvise_randomize`, and OOM adjustment helpers.

Control flow: the worker computes per-instance shared-memory bytes and object count, verifies `/dev/shm` writability on Linux, synchronizes start, and repeatedly forks a child. The child creates object names, opens/truncates/maps each object, reports names to the parent over a pipe, touches and optionally locks pages, forks a small helper to test inherited mappings, exercises fallocate modes, restores size, checks `fstat`, applies permission/ownership changes, verifies page-pattern memory, then unmaps/unlinks and reports freed names. The parent tracks names, kills/reaps the child, treats SIGKILL as possible OOM, restarts as needed, and unlinks any leftover objects.

State and persistence behavior: POSIX shm objects persist by name until `shm_unlink`, so the parent keeps a name ledger for cleanup after OOM or child death. Child state includes arrays of mapped addresses and names. No final durable files should remain.

Dependencies and integration points: registered as `CLASS_VM | CLASS_OS | CLASS_IPC`, always verify, with `shm-bytes`, `shm-mlock`, and `shm-objs` options. It depends on librt/POSIX shm support, stress-ng OOM handling, mmap/mincore/madvise helpers, filesystem access to `/dev/shm`, and global option flags.

Risks and test signals: risks are OOM restarts, `/dev/shm` mount/permission failures, leaked objects, shared-memory mapping behavior differences, and unsupported fallocate modes. Test signals include memory check failures, bad size from `fstat`, failed unlink/reporting, or unbounded restarts.
