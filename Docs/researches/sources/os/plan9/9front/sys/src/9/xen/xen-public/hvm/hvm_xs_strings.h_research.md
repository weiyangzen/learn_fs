# File Research: sources/os/plan9/9front/sys/src/9/xen/xen-public/hvm/hvm_xs_strings.h

Imported Xen public HVM xenstore key definitions.

Purpose:
- Defines xenstore string paths consumed by `hvmloader` for BIOS, ACPI, SMBIOS, generation ID, and related HVM firmware configuration.

Key content:
- Defines `hvmloader` root keys for BIOS choice, generation-id address, and memory relocation.
- Defines ACPI passthrough address/length keys.
- Defines SMBIOS passthrough address/length and default battery key.
- Defines BIOS/system/enclosure/battery string override keys and OEM string format.

Integration:
- HVM firmware/toolstack ABI only; not used by 9front’s PV xenstore client except as part of the vendored public header set.

Risks/notes:
- Xenstore key spelling is ABI; mismatches silently break firmware customization.
