<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XProtocol/XPtypes.hh -->
# sources/distributed-fs/xrootd/src/XProtocol/XPtypes.hh

Purpose: supplies the protocol integer and byte typedefs used by `XProtocol.hh` and `YProtocol.hh`. It exists to keep on-the-wire field sizes stable across historical C/C++ data models.

Important APIs/types/functions: `kXR_char`, `kXR_int16`, `kXR_unt16`, `kXR_int32`, `kXR_unt32`, `kXR_int64`, and `kXR_unt64`. It also defines compatibility probes `XR__INT16` and `XR__INT64` for LP32/ILP64-like environments.

Control flow: no functions. Preprocessor branches select a 32-bit signed/unsigned type based on detected platform model. Most normal platforms use `int`/`unsigned int` for 32-bit fields and `long long`/`unsigned long long` for 64-bit fields.

State and persistence behavior: all state is type-level. Persistence impact is high because these typedefs determine serialized XRootD and CMS protocol field widths.

Dependencies: no project includes beyond compiler/platform macros. It assumes platform types such as `int32`/`unsigned int32` exist in the ILP64 branch.

Integration points: every protocol struct in `XProtocol.hh` and `YProtocol.hh` is built from these aliases. Serialization, byte swapping, and protocol compatibility depend on these aliases matching the documented sizes.

Risks: unusual platform models may select rarely tested typedef paths. The header says only char and short are truly portable, but the protocol still depends on 32-bit and 64-bit aliases being exact. Any compiler where `int`, `long`, or `long long` widths differ from expectations can corrupt wire layouts.

Test signals: compile-time `sizeof` checks for all aliases; protocol struct size checks; cross-compilation sanity on LP32, LP64, and any supported ILP64 targets; serialization tests that compare known byte fixtures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XProtocol/XPtypes.hh -->
