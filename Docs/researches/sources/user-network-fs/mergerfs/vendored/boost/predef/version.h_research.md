# sources/user-network-fs/mergerfs/vendored/boost/predef/version.h

Purpose: Publishes the Boost.Predef component version.

Important APIs, types, and functions: Defines `BOOST_PREDEF_VERSION` as `BOOST_VERSION_NUMBER(1,15,1)`.

Control flow: Straight include guard plus inclusion of `version_number.h`; no conditional branches beyond the guard.

State and persistence behavior: Compile-time constant only.

Dependencies and integration points: Consumers compare this macro when they need a minimum Boost.Predef feature set.

Risks: It is the vendored Predef version, not the whole Boost distribution version and not mergerfs's version.

Test signals: No direct test hook; correctness is visible through compilation and version comparisons.
