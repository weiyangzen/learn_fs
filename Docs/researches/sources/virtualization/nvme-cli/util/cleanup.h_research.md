# File Research: sources/virtualization/nvme-cli/util/cleanup.h

Cleanup attribute helper macros for RAII-style cleanup in C.

Key elements:
- Defines `__cleanup(fn)` as GCC/Clang cleanup attribute.
- Provides cleanup helpers for:
  - `free`
  - `libnvme_free`
  - huge libnvme allocations
  - file descriptors greater than stderr
  - libnvme global contexts
  - libnvme controllers
  - `FILE *` via `fclose`
- Under `CONFIG_FABRICS`, adds URI and NVMf context cleanup helpers.

Role:
- Used throughout command code to reduce manual cleanup paths.
