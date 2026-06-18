# File Research: sources/os/plan9/9front/sys/src/9/xen/xen-public/nmi.h

Purpose: Xen public NMI ABI header. It defines x86 NMI reason bits and the `nmi_op` commands used to register or unregister a callback.

Key interfaces:
- Reason bits: I/O error, PCI SERR, legacy parity alias, unknown NMI.
- `XENNMI_register_callback` with `xennmi_callback.handler_address`.
- `XENNMI_unregister_callback`.

Integration notes: Depends on `xen.h` for guest handles and Xen integer types. Primarily useful to privileged/dom0 code.

Risk/attention points: Callback registration is documented as meaningful only for dom0 vcpu0; other callers receive `EINVAL`.
