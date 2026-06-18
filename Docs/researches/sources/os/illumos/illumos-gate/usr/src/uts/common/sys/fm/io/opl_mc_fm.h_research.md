# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fm/io/opl_mc_fm.h

This header defines FMA class and payload names for OPL memory-controller events.

Event classes:
- Base class is `MC_OPL_ERROR_CLASS` (`"asic.mac"`).
- Subclasses include `"ptrl"` and `"mi"`.
- Ereport definitions cover UE, CE, ICE, CMPE, MUE, and SUE.

Payload names:
- Board, bank, status, error address, error log, syndrome, DIMM slot, DRAM location, physical address, and fault type.
- Resource name is `"resource"`.
- `MC_OPL_NO_UNUM` is an empty string for absent unum data.

Dependencies and relationships:
- This is a platform-specific FMA protocol header for OPL memory hardware.
- It is a string-contract header, not an implementation header.
