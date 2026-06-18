# sources/user-network-fs/mergerfs/vendored/boost/predef/other.h

Purpose: Aggregates miscellaneous Boost.Predef detectors that are not operating-system, compiler, language, architecture, or library detectors.

Important APIs, types, and functions: It does not define new direct feature macros. It includes `boost/predef/other/endian.h`, `boost/predef/other/wordsize.h`, and `boost/predef/other/workaround.h`.

Control flow: The include guard permits normal one-time inclusion and also supports `BOOST_PREDEF_INTERNAL_GENERATE_TESTS`, matching other Boost.Predef aggregator headers.

State and persistence behavior: No runtime state. It introduces compile-time macro state from its included child headers.

Dependencies and integration points: Used by broader Boost.Predef aggregation to expose endianness, architecture word size, and workaround comparison helpers from one include.

Risks: Including this header can transitively include architecture and platform headers through `endian.h` and `wordsize.h`; this is expected but can alter available detection macros in translation units.

Test signals: Child headers carry their own `BOOST_PREDEF_DECLARE_TEST` declarations.
