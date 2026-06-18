# File Research: sources/os/plan9/9front/sys/src/9/xen/xen-public/features.h

Imported Xen public feature flag definitions.

Purpose:
- Defines feature bits reported by `XENVER_get_features` and referenced by Xen ELF feature notes.

Key content:
- Defines feature names for writable page tables, writable descriptor tables, auto-translated physmap, supervisor-mode kernel, PAE page directories above 4GB, MMU update preserve A/D, highmem assist, grant-table map available bits, HVM callback vector, HVM safe pvclock, HVM PIRQs, and dom0 support.
- Defines `XENFEAT_NR_SUBMAPS`.

Integration:
- Included by `version.h` in this Xen public tree.
- Feature names are also referenced by `elfnote.h`.
- Relevant for guest boot/feature negotiation, though the visible 9front Xen guest code mostly uses fixed PV paths.

Risks/notes:
- Feature-bit interpretation is negotiated with Xen; assuming a feature without checking can break on older hosts.
