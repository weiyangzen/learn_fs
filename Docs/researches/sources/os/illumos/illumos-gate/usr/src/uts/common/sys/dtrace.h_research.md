# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dtrace.h

This header defines the primary DTrace kernel, provider, helper, DOF, DIF, ioctl, and ABI-facing data contracts. Although marked private to DTrace/Solaris implementation, it is the central shared definition point for kernel DTrace providers, libdtrace-facing ioctls, and embedded DOF objects.

Key contents:
- Universal DTrace constants and identifiers for probes, enabled probes, aggregations, providers, predicate caches, and name-length limits.
- DIF instruction set definitions, register/table limits, built-in variable IDs, subroutine IDs, instruction packing/extraction macros, DIF types, and DIF variable metadata.
- DTrace action classes and action IDs, including regular tracing, process actions, destructive actions, kernel actions, speculation, and aggregation actions.
- Aggregation helpers for `quantize()`, `lquantize()`, `llquantize()`, and `ustack()` packed arguments.
- DOF object format definitions: file header, section headers, section types, relocation records, option records, provider/probe records, translator records, and DIFO representation.
- Enabling description structures: probe descriptions, predicate/action/ECB descriptions, record descriptions, enabled-probe descriptions, aggregation descriptions, and format descriptions.
- Runtime option identifiers and token values for buffer policy, buffer resize policy, sizes, rates, stack frames, zone, destructive mode, and aggregation display options.
- User/kernel buffer, record, status, configuration, fault, argument-description, stability, provider-attribute, and provider-privilege structures.
- DTrace pseudodevice ioctl numbers `DTRACEIOC_*` and helper-minor ioctl numbers `DTRACEHIOC_*`.
- Helper DOF model for user-level statically defined tracing and helper actions.
- Kernel-only provider API: `dtrace_pops_t`, provider mode flags, provider registration/unregistration, probe create/lookup/fire APIs, and meta-provider APIs.
- Kernel hooks used by DTrace for virtual time, fasttrap, module load/unload, helper cleanup/fork, CPU startup, debugger integration, xcalls, toxic ranges, panic, safe signals, instruction sizing, invalid-op handling, and CPU DTrace flags.

Dependencies:
- Includes `sys/types.h`, `sys/modctl.h`, `sys/processor.h`, `sys/systm.h`, `sys/ctf_api.h`, `sys/cyclic.h`, and `sys/int_limits.h` outside `_ASM`.
- Architecture-specific sections define x86 invalid-op constants and SPARC/x86 kernel hook prototypes.
- Uses C++ guards.

Research notes:
- This is ABI-sensitive despite private-interface warnings: DOF, DIF, ioctl payloads, ELF-embedded DOF, helper DOF, and provider contracts must match libdtrace, kernel DTrace, providers, and consumers.
- Several structures are explicitly bitness-neutral or use `DTRACE_PTR()` to preserve 32-bit consumer compatibility on 64-bit kernels.
- `dtrace_probe()` is documented as callable from nearly arbitrary kernel contexts, which drives many constraints on provider callbacks and DTrace internals.
- Filesystem relevance is indirect but important: DTrace is a major observability surface for VFS, storage, page cache, ZFS, and driver code. This header defines the provider and data contracts those components use for instrumentation.
