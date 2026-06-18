# File Research: sources/os/plan9/9front/sys/src/9/xen/xen-public/hvm/hvm_op.h

Imported Xen public HVM operation ABI.

Purpose:
- Defines `hvm_op` command IDs and argument structures for HVM parameter access, interrupt routing, memory typing/access, time, tracing, trap injection, and MSI injection.

Key content:
- Defines `HVMOP_set_param`/`get_param` with `struct xen_hvm_param`.
- Defines PCI INTx, ISA IRQ, and PCI link route updates.
- Defines `HVMOP_flush_tlbs`.
- Defines HVM memory types `HVMMEM_ram_rw`, `HVMMEM_ram_ro`, and `HVMMEM_mmio_dm`.
- Under Xen/tools guards, defines dirty VRAM tracking, modified-memory notification, and memory type setting.
- Defines `HVMOP_pagetable_dying`, `HVMOP_get_time`, and `HVMOP_xentrace`.
- Under Xen/tools guards, defines memory access modes, get/set access operations, trap injection, and MSI injection.
- Defines `HVMOP_get_mem_type`.

Integration:
- HVM/device-model ABI context; not used by the visible 9front PV guest runtime.
- Included by `hvm/params.h`.

Risks/notes:
- Several interfaces are explicitly tools-only and may change.
- Memory access and trap injection semantics are security-sensitive in control stacks.
