# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/devfm.h

This header defines `/dev/fm` ioctl interfaces and packed nvlist schemas for FMA consumers. It includes base types and nvpair.

It sets maximum input/output buffer sizes, driver version, version-key strings, and ioctl commands under `FM_IOC`. Generic commands include versions, page retire/status/unretire, and cache info. x86-specific commands include physical CPU info, CPU retire/status/unretire, legacy topology generation, and CPU PCI data.

`fm_ioc_data_t` carries interface version, input packed nvlist size/buffer, output packed nvlist size/buffer, and has a kernel-only 32-bit form. Most operation data is encoded as packed nvlist keys defined in this file.

The schema includes keys for page retire FMRI, CPU lists, chip/core/strand IDs, old status, topology legacy data, cache CPU count, physical CPU vendor/family/model/stepping/chip/core/strand/APIC/SMBIOS/root/revision/socket/cpuid/identifier string fields, cache metadata, and PCI data fabric records.

`fm_cache_info_type_t` describes data, instruction, and unified caches. Cache info keys include level, type, sets, ways, line size, total size, fully-associative boolean, synthetic cache id, and x86 APIC shift.

Research notes:
- The ioctl payload is a packed nvlist ABI; key names are as important as structs.
- Some operations are architecture-gated under `__x86`.
- Buffer-size constants constrain user/kernel copy behavior for FMA management data.
