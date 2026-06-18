<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/hardware/simd.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/hardware/simd.h

## Purpose

`sources/user-network-fs/mergerfs/vendored/boost/predef/hardware/simd.h` is the aggregate SIMD hardware detector. It includes the x86, x86 AMD extension, ARM, and PPC SIMD detectors and exposes one overall `BOOST_HW_SIMD` value when exactly one architecture family is active.

## Important APIs, Types, and Functions

The main macros are `BOOST_HW_SIMD`, `BOOST_HW_SIMD_AVAILABLE`, and `BOOST_HW_SIMD_NAME`. Direct includes are `boost/predef/hardware/simd/x86.h`, `boost/predef/hardware/simd/x86_amd.h`, `boost/predef/hardware/simd/arm.h`, `boost/predef/hardware/simd/ppc.h`, `boost/predef/version_number.h`, `boost/predef/hardware/simd.h`, `iostream`, `boost/predef/hardware/simd.h`, `iostream`, `boost/predef/hardware/simd.h`, `iostream`, `boost/predef/hardware/simd.h`, `iostream`, `boost/predef/detail/test.h`.

## Control Flow

After including architecture-specific SIMD headers, the file errors if incompatible SIMD architecture families are simultaneously detected. If both `BOOST_HW_SIMD_X86` and `BOOST_HW_SIMD_X86_AMD` are available, it chooses the larger version. Otherwise it copies the single active architecture value or falls back to `BOOST_VERSION_NUMBER_NOT_AVAILABLE`.

## State and Persistence Behavior

The file has no runtime state. Its result is a translation-unit-local preprocessor macro derived from the target flags and architecture macros visible during compilation.

## Dependencies and Integration Points

It is included by `boost/predef/hardware.h` and ultimately by `boost/predef.h`. Code that only needs to know whether any SIMD extension is enabled can include this aggregate instead of checking each architecture-specific header.

## Risks and Edge Cases

The mutual-exclusion check assumes a single target architecture. Unusual compiler environments that expose multiple architecture feature sets can trigger the explicit error. The x86/x86_amd merge needs numeric version ordering to remain consistent with the version tables.

## Test Signals

Build small probes with no SIMD flags, with x86 SSE/AVX flags, with ARM NEON target flags, and with PPC VMX/VSX flags. Confirm `BOOST_HW_SIMD_AVAILABLE` and the selected numeric value match the strongest enabled extension.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/hardware/simd.h -->
