# File Research: sources/virtualization/nvme-cli/libnvme/src/nvme/compiler-attributes.h

Central header for compiler visibility and annotation attributes.

Macros:
- `__libnvme_public`: marks a symbol with default visibility for shared library ABI export.
- `__libnvme_weak`: declares weak symbols for optional overrides/platform hooks.
- `__libnvme_unused`: suppresses unused warnings for intentionally unused symbols or parameters.

Integration:
- Used by generated accessors, filters, ioctl wrappers, fabrics, and crypto public APIs.
- Supports builds with `-fvisibility=hidden` by making exported symbols explicit.

Risks:
- GCC/Clang attribute syntax is assumed.
- Public ABI depends on consistent use of `__libnvme_public`; omitting it can hide intended API symbols.
