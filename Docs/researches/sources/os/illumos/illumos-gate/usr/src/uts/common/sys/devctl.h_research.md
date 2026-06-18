# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/devctl.h

This header defines the devctl ioctl ABI used by libdevice, nexus drivers, attachment-point management, power-management tests/controls, and LED controls. It includes base types and nvpair.

`struct devctl_iocdata` is the ioctl payload shared between libdevice interfaces and nexus driver devctl handling. It stores command, flags, copyout buffer, packed user nvlist pointer/size, child node name, and unit address. A 32-bit version exists for syscall32. `DEVCTL_MAX_NVL_USERSZ` limits packed user attributes to 64 KiB.

Attachment point state enums describe receptacle state, occupant state, and condition. `devctl_ap_state_t` and its 32-bit form report AP state, condition, last-change time, error code, and transition flag.

The ioctl namespace is `DEVCTL_IOC`. Commands cover bus quiesce/unquiesce/reset/getstate/configure/unconfigure/device-create, device online/offline/getstate/reset/remove, AP connect/disconnect/insert/remove/configure/unconfigure/getstate/control, PM busy/idle/power transitions/test controls, PROM printf, suspend failure simulation, resume power-change markers, and LED set/get/count.

State bit definitions report device online/busy/offline/down and bus active/quiesced/shutdown. `IS_DEVCTL()` checks the ioctl range. `DC_DEVI_NODENAME`, construction/offline flags, and LED control structures/constants round out the ABI.

Research notes:
- This header is user/kernel ABI and should be changed cautiously.
- Applications are expected to use libdevice rather than direct structure access.
- Several PM ioctls are diagnostic/test hooks and not generic hotplug controls.
