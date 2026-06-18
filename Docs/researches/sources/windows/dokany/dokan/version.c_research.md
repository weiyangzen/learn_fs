# File Research: sources/windows/dokany/dokan/version.c

Exposes user library and driver version queries.

Key behavior:
- `DokanVersion()` returns compile-time `DOKAN_VERSION`.
- `DokanDriverVersion()` sends `FSCTL_GET_VERSION` to `DOKAN_GLOBAL_DEVICE_NAME`.
- On device query failure, logs and returns `0`.

Role:
- Supports runtime compatibility checks between user-mode library and installed Dokan driver.
