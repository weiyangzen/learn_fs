<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/hardware/simd/x86/versions.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/hardware/simd/x86/versions.h

## Purpose

`sources/user-network-fs/mergerfs/vendored/boost/predef/hardware/simd/x86/versions.h` defines symbolic Boost.Predef version constants for X86 SIMD instruction-set levels. The constants let callers compare `BOOST_HW_SIMD_*` detector values without hard-coding `BOOST_VERSION_NUMBER` tuples.

## Important APIs, Types, and Functions

Version macros in this file include `BOOST_HW_SIMD_X86_MMX_VERSION`, `BOOST_HW_SIMD_X86_SSE_VERSION`, `BOOST_HW_SIMD_X86_SSE2_VERSION`, `BOOST_HW_SIMD_X86_SSE3_VERSION`, `BOOST_HW_SIMD_X86_SSSE3_VERSION`, `BOOST_HW_SIMD_X86_SSE4_1_VERSION`, `BOOST_HW_SIMD_X86_SSE4_2_VERSION`, `BOOST_HW_SIMD_X86_AVX_VERSION`, `BOOST_HW_SIMD_X86_FMA3_VERSION`, `BOOST_HW_SIMD_X86_AVX2_VERSION`, `BOOST_HW_SIMD_X86_MIC_VERSION`. Direct includes are `boost/predef/version_number.h`.

## Control Flow

There is no conditional detection. The header is a constant table guarded by an include guard; detector headers include it and then choose the highest enabled version based on compiler predefined feature macros.

## State and Persistence Behavior

The file is preprocessor-only and stateless. The constants persist as macros in the current translation unit.

## Dependencies and Integration Points

It integrates with the sibling SIMD detector for the same architecture and with `boost/predef/hardware/simd.h`, which selects an overall `BOOST_HW_SIMD` value from architecture-specific detections.

## Risks and Edge Cases

Incorrect ordering or numeric values would break range comparisons such as `>= SSE2_VERSION`. New instruction-set levels require updates here and in the detector header that maps compiler macros to these constants.

## Test Signals

Preprocessor tests should assert monotonic ordering of the version constants and compile detector checks under compiler flags that enable representative SIMD levels.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/hardware/simd/x86/versions.h -->
