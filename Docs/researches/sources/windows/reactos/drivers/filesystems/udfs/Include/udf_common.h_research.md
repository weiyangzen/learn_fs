# File Research: sources/windows/reactos/drivers/filesystems/udfs/Include/udf_common.h

## Purpose
Defines common UDFS media classes, the central `VCB` volume-control block, global driver data, and major VCB/global flags.

## Main Contents
- `UDFFSD_MEDIA_TYPE` classifies media such as HDD, CDR, CDRW, CDROM, ZIP, floppy, DVDR, and DVDRW.
- `VCB` combines kernel FCB-compatible fields, mounted-volume state, physical media geometry, track/write-cache state, UDF logical-volume metadata, bitmaps, sparing/VAT information, registry/config-derived policy, and compatibility flags.
- `UDFData` stores global driver objects, recognizer/device objects, zones/lookaside-like storage, delayed-close queues, global strings, cache defaults, and flags.
- Defines `UDF_VCB_FLAGS_*` for mount/read-only/raw/device/cache/eject/dead state.
- Defines `UDF_VCB_IC_*` compatibility and policy flags for timestamps, write behavior, sync-cache quirks, bad seek/MRW/FP addressing workarounds, dirty/read-only handling, and blank-CD display.

## Build Modes
Large portions of `VCB` and `UDFData` exist only with `_UDF_STRUCTURES_H_`; `_BROWSE_UDF_` adds logical UDF metadata, allocation maps, sparing, VAT, and verifier state. Formatter/user builds use reduced structures.

## Architectural Role
This header is the shared state contract for files like `phys_lib.cpp`; most physical I/O decisions mutate fields declared here.

## Notable Risks
Because `VCB` is broad and conditional, structure layout depends strongly on compile-time defines. Code sharing between kernel, formatter, and browse builds must use matching defines.
