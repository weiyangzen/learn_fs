# File Research: sources/virtualization/nvme-cli/libnvme/src/libnvme-mi.h

This public aggregate header exposes libnvme MI APIs.

Content:
- C++ guards with `extern "C"`.
- Includes:
  - `nvme/lib.h`
  - `nvme/mi.h`
  - `nvme/nvme-types.h`
  - `nvme/nvme-cmds.h`

Integration role:
- Installed when MI support is enabled.
- Used by MI examples such as `mi-mctp.c`, `mi-conf.c`, and `mi-mctp-ae.c`.
