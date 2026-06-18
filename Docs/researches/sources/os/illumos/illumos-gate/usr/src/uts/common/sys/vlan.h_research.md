# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/vlan.h

## Role

`vlan.h` defines media-independent VLAN tag constants and bitfield helpers.

## Key Interfaces

The header defines:
- VLAN tag size `VLAN_TAGSZ = 4`.
- TPID `VLAN_TPID = 0x8100`.
- masks, sizes, and shifts for VLAN ID, CFI, and priority.
- valid VLAN ID range: none `0`, minimum `1`, maximum `4094`.

Macros:
- `VLAN_TCI(pri, cfi, vid)` constructs a tag-control-information value.
- `VLAN_PRI(tci)`, `VLAN_CFI(tci)`, and `VLAN_ID(tci)` extract fields.
- `VLAN_MBLKPRI(mp)` maps a STREAMS message band to VLAN priority using 32 bands per priority and clamps out-of-range values to zero.

## Research Notes

The macros do not validate input ranges. Callers should sanitize priority, CFI, and VLAN ID before constructing a TCI.
