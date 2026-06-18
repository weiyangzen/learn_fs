# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ddimapreq.h

This header defines the private DDI bus mapping request structure and related return codes. It includes mmap protections and DDI types.

Kernel-only `ddi_map_obj_t` can hold either an rnumber or a `regspec *`; `ddi_map_type_t` distinguishes those forms. `ddi_map_op_t` covers unlocked map, locked map, handle-only map, unmap, and unlock-without-unmap operations. `ddi_map_req_t` packages the operation, object type/value, mapping flags, protection bits, access-handle pointer, and version.

Mapping version is `DDI_MAP_VERSION`. Mapping flags distinguish user mapping, kernel mapping, device mapping, and a platform-reserved high-bit x86 extended regspec flag.

The public error codes are negative values for generic errors, unimplemented operator, no resources, unsupported operation, regspec/rnumber range errors, and invalid input.

Research notes:
- This is a bus nexus/private framework contract, not a typical driver API.
- The x86 extended regspec bit is reserved for children of the x86 root nexus.
- Mapping semantics depend on `regspec` layout from `ddi_impldefs.h` and mmap protection flags.
