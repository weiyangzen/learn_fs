# File Research: sources/os/plan9/9front/sys/src/9/xen/xen-public/dom0_ops.h

Imported Xen legacy dom0 compatibility ABI.

Purpose:
- Provides pre-`0x00030204` compatibility aliases from legacy `dom0_op` names to platform-operation names.

Key content:
- Errors out for newer interface versions because it is compatibility-only.
- Maps `DOM0_SETTIME`, memtype operations, microcode update, and platform quirks to `XENPF_*` equivalents.
- Defines legacy unsupported `DOM0_MSR` and `DOM0_PHYSICAL_MEMORY_MAP` structures for API compatibility.
- Defines `struct dom0_op` with command, interface version, and a 128-byte union payload.

Integration:
- Not part of the 9front guest’s runtime fast path.
- Vendored for Xen public header completeness and older control-stack compatibility.

Risks/notes:
- Deliberately version-gated legacy interface.
- Should not be used in new guest code.
