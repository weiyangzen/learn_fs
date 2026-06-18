<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/hardware/simd/arm.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/hardware/simd/arm.h

## Purpose

`sources/user-network-fs/mergerfs/vendored/boost/predef/hardware/simd/arm.h` detects SIMD hardware support for its architecture family and reports the highest enabled extension as a Boost.Predef version macro. SIMD detection is driven by compiler target flags and predefined feature macros.

## Important APIs, Types, and Functions

Primary reported macros are `BOOST_HW_SIMD_ARM`. Related macros include `BOOST_HW_SIMD_ARM`, `BOOST_HW_SIMD_ARM_AVAILABLE`, `BOOST_HW_SIMD_ARM_NAME`. Display-name macros are `BOOST_HW_SIMD_ARM_NAME` "ARM SIMD". Direct includes are `boost/predef/version_number.h`, `boost/predef/hardware/simd/arm/versions.h`, `boost/predef/detail/test.h`.

## Control Flow

The detector starts with its `BOOST_HW_SIMD_*` macro set to not available, then checks architecture/compiler feature symbols such as `__ARM_NEON__`, `__aarch64__`, `_M_ARM`, `_M_ARM64`. Matching branches assign the newest supported version constant from the sibling `versions.h` table, define `*_AVAILABLE`, and register a predef test.

## State and Persistence Behavior

There is no runtime state. Detection results are macros that persist only for the current translation unit and depend on compiler options such as x86 `-mavx`, ARM NEON flags, or PPC VMX/VSX flags.

## Dependencies and Integration Points

This file feeds `boost/predef/hardware/simd.h`, which chooses the overall `BOOST_HW_SIMD` value and guards against incompatible multi-architecture SIMD detections. Mergerfs can use it through vendored Boost for conditional compilation of target-specific code.

## Risks and Edge Cases

SIMD macros are inclusive and compiler-option dependent, so a host CPU may support an instruction set that is not reported unless the compiler target enables it. Cross-compilation can expose target macros unrelated to the build host. Visual C++ and GCC/Clang expose different granularity.

## Test Signals

Compile preprocessor probes with representative target flags and assert the selected `BOOST_HW_SIMD_*` value. Include negative builds with no SIMD flags and cross-target builds to ensure only the intended architecture-specific availability macro is set.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/hardware/simd/arm.h -->
