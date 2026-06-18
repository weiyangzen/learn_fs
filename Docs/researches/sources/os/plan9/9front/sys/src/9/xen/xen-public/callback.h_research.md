# File Research: sources/os/plan9/9front/sys/src/9/xen/xen-public/callback.h

Imported Xen public callback registration ABI.

Purpose:
- Defines `callback_op` command IDs, callback types, flags, and register/unregister structures.

Key content:
- Defines callback types for event, failsafe, syscall, deprecated sysenter, NMI, sysenter, and syscall32.
- Defines `CALLBACKF_mask_events`.
- Defines `CALLBACKOP_register` with `struct callback_register { type, flags, xen_callback_t address }`.
- Defines `CALLBACKOP_unregister` with `struct callback_unregister`.
- Keeps older interface-version compatibility for `CALLBACKTYPE_sysenter`.

Integration:
- 9front currently uses the older `HYPERVISOR_set_callbacks` path in `trap.c` and low-level callback assembly, but this header supplies the newer public callback-op ABI.
- Depends on architecture-defined `xen_callback_t`.

Risks/notes:
- Callback address type is architecture-specific.
- Event masking semantics differ for event/NMI callbacks versus other callback types.
