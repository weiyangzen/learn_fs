# File Research: sources/os/plan9/9front/sys/src/9/xen/xen-public/hvm/hvm_info_table.h

Imported Xen public HVM information-table ABI.

Purpose:
- Defines the HVM info table placed in guest memory by the HVM domain builder.

Key content:
- Defines `HVM_INFO_PFN`, `HVM_INFO_OFFSET`, `HVM_INFO_PADDR`, and `HVM_MAX_VCPUS`.
- Defines `struct hvm_info_table` with signature, length, checksum, APIC mode, VCPU count, low/reserved/high memory boundaries, and boot-online VCPU bitmap.

Integration:
- HVM domain-builder/firmware ABI; not part of the current 9front PV block/net driver path.

Risks/notes:
- Structure layout and checksum semantics are boot ABI.
