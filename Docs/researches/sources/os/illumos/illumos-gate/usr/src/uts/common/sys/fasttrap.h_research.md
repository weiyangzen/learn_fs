# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fasttrap.h

## Role

`fasttrap.h` defines the user/kernel ioctl-facing ABI for DTrace fasttrap probes, including probe creation specs, instruction queries, and PT_SUNWDTRACE size linkage.

## Definitions

- Includes ISA-specific fasttrap definitions, DTrace definitions, and base types.
- Defines ioctl base `FASTTRAPIOC` and commands `FASTTRAPIOC_MAKEPROBE` and `FASTTRAPIOC_GETINSTR`.
- Defines `fasttrap_probe_type_t` with entry, return, offsets, post-offsets, and is-enabled probe types.
- `fasttrap_probe_spec_t` carries pid, probe type, function and module names, PC, function/probe size, offset count, and variable offset list.
- `fasttrap_instr_query_t` carries PC, pid, and returned instruction.
- Defines `PT_SUNWDTRACE_SIZE` from `FASTTRAP_SUNWDTRACE_SIZE`, tying kernel exec handling to the runtime linker/libc early-process tracing data object.
