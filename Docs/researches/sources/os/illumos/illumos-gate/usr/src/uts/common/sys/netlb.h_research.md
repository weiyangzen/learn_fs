# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/netlb.h

Generic network driver loopback-test ioctl ABI header.

Key responsibilities:
- Defines loopback ioctl base and commands to get loopback-info size, get loopback-info table, get current mode, and set current mode.
- Documents the intended user flow for discovering available loopback modes, selecting/restoring modes, and running tests.
- Defines loopback info size type.
- Defines generic loopback mode types: normal, external, and internal.
- Defines `lb_property_t` entries with type, string key, and numeric value.

Dependencies:
- Uses `uint32_t` from surrounding system types.

Notable risks:
- Drivers expose mode keys/values through this ABI, so userland test tools depend on stable interpretation.
- Mode changes affect hardware test behavior and must be restored after diagnostics.
