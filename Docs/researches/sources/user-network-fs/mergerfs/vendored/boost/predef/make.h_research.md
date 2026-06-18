<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/make.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/make.h

## Purpose

`sources/user-network-fs/mergerfs/vendored/boost/predef/make.h` defines the Boost.Predef version-conversion macro library. Vendor predefined macros often encode versions as packed decimal, packed hexadecimal, or dates; this header normalizes those encodings into `BOOST_VERSION_NUMBER(major, minor, patch)` values.

## Important APIs, Types, and Functions

The public surface is the `BOOST_PREDEF_MAKE_*` macro family. This file defines 31 conversion macros, including `BOOST_PREDEF_MAKE_0X_VRP(V) BOOST_VERSION_NUMBER((V&0xF00)>>8,(V&0xF0)>>4,(V&0xF))`, `BOOST_PREDEF_MAKE_0X_VVRP(V) BOOST_VERSION_NUMBER((V&0xFF00)>>8,(V&0xF0)>>4,(V&0xF))`, `BOOST_PREDEF_MAKE_0X_VRPP(V) BOOST_VERSION_NUMBER((V&0xF000)>>12,(V&0xF00)>>8,(V&0xFF))`, `BOOST_PREDEF_MAKE_0X_VVRR(V) BOOST_VERSION_NUMBER((V&0xFF00)>>8,(V&0xFF),0)`, `BOOST_PREDEF_MAKE_0X_VRRPPPP(V) BOOST_VERSION_NUMBER((V&0xF000000)>>24,(V&0xFF0000)>>16,(V&0xFFFF))`, `BOOST_PREDEF_MAKE_0X_VVRRP(V) BOOST_VERSION_NUMBER((V&0xFF000)>>12,(V&0xFF0)>>4,(V&0xF))`, `BOOST_PREDEF_MAKE_0X_VRRPP000(V) BOOST_VERSION_NUMBER((V&0xF0000000)>>28,(V&0xFF00000)>>20,(V&0xFF000)>>12)`, `BOOST_PREDEF_MAKE_0X_VVRRPP(V) BOOST_VERSION_NUMBER((V&0xFF0000)>>16,(V&0xFF00)>>8,(V&0xFF))`, `BOOST_PREDEF_MAKE_10_VPPP(V) BOOST_VERSION_NUMBER(((V)/1000)%10,0,(V)%1000)`, `BOOST_PREDEF_MAKE_10_VVPPP(V) BOOST_VERSION_NUMBER(((V)/1000)%100,0,(V)%1000)`, `BOOST_PREDEF_MAKE_10_VR0(V) BOOST_VERSION_NUMBER(((V)/100)%10,((V)/10)%10,0)`, `BOOST_PREDEF_MAKE_10_VRP(V) BOOST_VERSION_NUMBER(((V)/100)%10,((V)/10)%10,(V)%10)`, `BOOST_PREDEF_MAKE_10_VRP000(V) BOOST_VERSION_NUMBER(((V)/100000)%10,((V)/10000)%10,((V)/1000)%10)`, `BOOST_PREDEF_MAKE_10_VRPPPP(V) BOOST_VERSION_NUMBER(((V)/100000)%10,((V)/10000)%10,(V)%10000)`, `BOOST_PREDEF_MAKE_10_VRPP(V) BOOST_VERSION_NUMBER(((V)/1000)%10,((V)/100)%10,(V)%100)`, `BOOST_PREDEF_MAKE_10_VRR(V) BOOST_VERSION_NUMBER(((V)/100)%10,(V)%100,0)`, `BOOST_PREDEF_MAKE_10_VRRPP(V) BOOST_VERSION_NUMBER(((V)/10000)%10,((V)/100)%100,(V)%100)`, `BOOST_PREDEF_MAKE_10_VRR000(V) BOOST_VERSION_NUMBER(((V)/100000)%10,((V)/1000)%100,0)`. Date helpers include `BOOST_PREDEF_MAKE_DATE`, `BOOST_PREDEF_MAKE_YYYYMMDD`, `BOOST_PREDEF_MAKE_YYYY`, and `BOOST_PREDEF_MAKE_YYYYMM`. Direct includes are `boost/predef/detail/test.h`.

## Control Flow

There is no branching detection logic. Each macro applies integer division, modulo, or bit masking/shifting to decompose a vendor value and recompose it with `BOOST_VERSION_NUMBER`. Date macros store years relative to the 1970 epoch used by Boost.Predef version numbering.

## State and Persistence Behavior

The header is preprocessor-only. It stores no runtime state and has no side effects other than making conversion macros available in the current translation unit.

## Dependencies and Integration Points

Nearly every concrete Predef detector depends on this file when its vendor macro carries a structured version. Compiler, OS, architecture, language, and library headers call these macros to keep their `BOOST_*` values comparable.

## Risks and Edge Cases

A wrong conversion format silently reports an incorrect version while still marking the feature available. Date conversion intentionally defaults missing month/day values to January 1. Packed macro arithmetic assumes the vendor value is numeric and available to the preprocessor.

## Test Signals

Unit preprocessor tests should feed representative hexadecimal, decimal, and date values into each conversion macro and compare the result with expected `BOOST_VERSION_NUMBER` values. Detector-specific tests indirectly cover the macros by checking known compiler/library version macros.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/make.h -->
