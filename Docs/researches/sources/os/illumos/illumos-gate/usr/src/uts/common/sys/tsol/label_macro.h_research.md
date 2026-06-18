# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/tsol/label_macro.h

## Purpose
Low-level Trusted Extensions binary label layout and macro operations.

## Main Interfaces
- Defines classification, compartment, marking, sensitivity label, CMW label, clearance, and label range implementation structures.
- Defines `NMLP_MAX`, `NSLS_MAX`, label type IDs, classification bounds `LOW_CLASS` and `HIGH_CLASS`, and empty/universal bit sets.
- Defines type/access macros such as `_MTYPE`, `_MSETTYPE`, `_MGETTYPE`, `_MEQUAL`, `LCLASS`, `LCLASS_SET`, `ICLASS`, and `ICLASS_SET`.
- Defines label relation macros `BLTYPE`, `BLEQUAL`, `BLDOMINATES`, `BLSTRICTDOM`, and `BLINRANGE`.
- Defines label combination and initialization macros `BLMAXIMUM`, `BLMINIMUM`, `BCLLOW`, `BSLLOW`, `BSLHIGH`, `BILLOW`, `BCLEARLOW`, `BCLEARHIGH`, `BSLUNDEF`, and `BCLEARUNDEF`.
- Defines conversion macros such as `BCLTOSL`, `BCLTOIL`, `GETCSL`, `SETCSL`, `SETBLTYPE`, and `GETBLTYPE`.

## Dependencies And Relationships
Includes `sys/types.h`; included by `tsol/label.h` and other Trusted Extensions headers. It supplies the inlined primitive operations used by higher-level label APIs.

## Research Notes
This header is macro-heavy and layout-sensitive. It trades function calls for direct structure access, so type correctness and endian/bitset assumptions matter when modifying labels.
