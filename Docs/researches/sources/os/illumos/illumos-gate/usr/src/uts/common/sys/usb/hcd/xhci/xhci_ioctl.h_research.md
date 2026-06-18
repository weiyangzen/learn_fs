# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/hcd/xhci/xhci_ioctl.h

Private xHCI ioctl header. It defines the ioctl command namespace and three private commands: read port status/control registers, set port link state, and clear port state.

The structures are `xhci_ioctl_portsc_t`, containing up to 256 `PORTSC` values, `xhci_ioctl_setpls_t`, containing a port and target port-link state, and `xhci_ioctl_clear_t`, containing a port.

This is a small diagnostic/control surface. Because it exposes low-level port manipulation, implementation code using it must validate port indices and carefully preserve write-one-to-clear register semantics.
