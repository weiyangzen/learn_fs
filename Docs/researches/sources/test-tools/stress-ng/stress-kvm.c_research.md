# sources/test-tools/stress-ng/stress-kvm.c

Purpose: implements `kvm`, a `/dev/kvm` stressor that repeatedly creates a tiny VM, maps guest memory, creates one vCPU, runs a minimal architecture-specific guest loop, handles exits, and destroys all resources.

Important APIs/types/functions: `stress_kvm_open()` handles `/dev/kvm` access and skip reporting; `stress_kvm_supported()` probes availability. `kvm_kernel[]` contains tiny guest code for x86, ARM64, or RISC-V. Main KVM APIs include `KVM_CREATE_VM`, `KVM_SET_USER_MEMORY_REGION`, `KVM_CREATE_VCPU`, register setup ioctls, `KVM_GET_VCPU_MMAP_SIZE`, vCPU `mmap`, and `KVM_RUN`.

Control flow: after sync-start, each iteration opens `/dev/kvm`, optionally logs API version, creates a VM, mmaps one page of guest memory, registers it at the architecture physical base, optionally maps readonly MMIO memory for ARM/RISC-V, creates vCPU, copies guest code, initializes registers, maps `struct kvm_run`, and runs up to 1000 exits. x86 handles port I/O exits until a byte reaches `0xff`; ARM/RISC-V count MMIO exits. Success increments bogo ops before teardown.

State and persistence behavior: state is transient kernel VM/vCPU objects, anonymous memory mappings, fds, and guest register state. All are closed/unmapped each iteration.

Dependencies and integration points: gated to Linux with `linux/kvm.h` and supported architecture macros. Uses stress-ng capability checks, mmap, madvise, arch helpers, and process state. Registered as `CLASS_DEV | CLASS_OS`.

Risks: `/dev/kvm` availability, permissions, nested virtualization, architecture register ABI, and KVM API support vary widely. Error paths must close multiple partially initialized fds and mappings. ARM/RISC-V MMIO unmap uses page-size-sensitive cleanup and should be checked carefully.

Test signals: run in a VM host with KVM access, confirm skip without `/dev/kvm`, bogo increments only on successful guest exits, no fd/mmap leaks over repeated iterations, and no unexpected ioctl failures under `--verify`.
