# File Research: sources/os/bsd/freebsd-src/sys/sys/iov.h

Defines the public ioctl ABI and nvlist schema conventions for PCI SR-IOV configuration. It names top-level schema/config sections (`PF`, `VF`, `DRIVER`, `IOV`) and parameter metadata keys (`TYPE`, `DEFAULT`, `REQUIRED`).

The long embedded schema comments specify the accepted packed-nvlist format, validation rules, supported parameter types, VF key naming (`VF-<n>`), required/default behavior, and example schema/config layouts. These comments are effectively the ABI contract for userland SR-IOV management tools.

`struct pci_iov_schema` returns packed schema plus length/error; `struct pci_iov_arg` passes packed config. Ioctls are `IOV_CONFIG`, `IOV_DELETE`, and `IOV_GET_SCHEMA`.
