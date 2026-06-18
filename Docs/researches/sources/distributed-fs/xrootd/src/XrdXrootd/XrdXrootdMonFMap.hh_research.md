# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdMonFMap.hh

Purpose: declares the active-file slot map used by file-stat monitoring to track `XrdXrootdFileStats` objects efficiently.

Important APIs/types/functions: `cvPtr` union stores either a raw long, next-free pointer, or stats pointer. Constants define `mapNum` (`128` maps), per-map `fmSize` (`512` slots), lock-yield hold count, masks, and shift values. Public methods are `Insert`, `Free`, and `Next`.

Control flow: callers use the returned slot number with `fmShft`/`fmMask` to encode a map/slot cookie in file stats. Iteration is cursor-driven by an integer reference.

State and persistence behavior: each instance owns an optional allocated slot array plus a free-list head. State is process-memory only and mirrors currently open monitored files.

Dependencies: forward declaration of `XrdXrootdFileStats`.

Integration points: embedded as the static `fmMap` array in `XrdXrootdMonFile`; encoded entries are stored in `XrdXrootdFileStats::MonEnt`.

Risks: callers must use the constants consistently when packing/unpacking `MonEnt`. No copy prevention is declared, so accidental copying would duplicate pointer/free-list state. The class relies on external synchronization.

Test signals: cookie packing/unpacking across map boundaries, map capacity at 512 slots, high-water behavior in `XrdXrootdMonFile`, and accidental duplicate/free handling.
