# File Research: sources/os/plan9/9front/sys/src/9/xen/xen-public/arch-x86/xen-mca.h

Imported Xen public x86 Machine Check Architecture ABI header.

Purpose:
- Defines Xen MCA hypercall interface, event flags, machine-check info records, recovery actions, and injection commands.

Key content:
- MCA interface version, urgent/nonurgent/ack flags, result codes, and `VIRQ_MCA`.
- Record types for global, bank, extended MSR, recovery, and logical CPU machine-check information.
- `mc_info` container and lookup macros for iterating typed records.
- Hypercall command structures for fetch, notifydomain, physcpuinfo, MSR injection, MCE injection, and v2 injection.
- Top-level `xen_mc` command union.

Integration:
- Public Xen ABI support header; relevant for privileged tooling or machine-check event handling, not actively used by the small frontend files in this batch.

Risks/notes:
- Macro iteration depends on trusted record sizes from Xen; consumers should validate inputs if exposed to untrusted domains/tools.
