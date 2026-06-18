# File Research: sources/os/bsd/netbsd-src/lib/libnvmm/libnvmm.c

Implements the main userland NVMM library. It opens `/dev/nvmm`, verifies kernel/library version compatibility, creates/destroys machines and vCPUs, maps communication pages, manages guest physical/HVA mappings, caches vCPU state requests, injects events, runs vCPUs, exposes control ioctls, and stops vCPUs.

Important dependencies: `nvmm.h`, system `ioctl`, `mmap`, `queue`, `fcntl`, `errno`, `machine/vmparam.h`, and architecture-specific `libnvmm_x86.c` on x86_64.

Main behavior:
- `nvmm_init()` opens `/dev/nvmm` read-only; `nvmm_root_init()` opens write-only; both call `nvmm_capability()` and require `NVMM_KERN_VERSION`.
- Machine creation allocates a tracked GPA mapping list and per-vCPU communication page array before issuing `NVMM_IOC_MACHINE_CREATE`.
- vCPU creation issues `NVMM_IOC_VCPU_CREATE`, maps the shared communication page, and points `vcpu->state`, `event`, and `stop` into it.
- GPA mappings are tracked locally to reject overlapping guest physical ranges and to support `nvmm_gpa_to_hva()`.
- `nvmm_vcpu_getstate()` avoids ioctl work if requested flags are already cached; `nvmm_vcpu_setstate()` marks state as committed and cached.
- `nvmm_vcpu_run()` issues `NVMM_IOC_VCPU_RUN` and copies the returned exit data into `vcpu->exit`.

Notable risks: on `nvmm_gpa_map()` or `nvmm_gpa_unmap()` ioctl failure after local state change, the library calls `abort()` because it cannot recover. The local overlap validator ignores HVA overlap and only enforces GPA uniqueness. `nvmm_machine_destroy()` only frees local area/page structures after a successful kernel destroy.
