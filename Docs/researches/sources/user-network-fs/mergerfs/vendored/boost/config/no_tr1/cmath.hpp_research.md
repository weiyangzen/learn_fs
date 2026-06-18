# sources/user-network-fs/mergerfs/vendored/boost/config/no_tr1/cmath.hpp

Purpose: includes the real standard `<cmath>` while preventing recursive inclusion through Boost.TR1 wrapper paths.

Important APIs/macros: defines include guard `BOOST_CONFIG_CMATH`. If `BOOST_TR1_NO_RECURSION` is not already defined, it defines it and records ownership with `BOOST_CONFIG_NO_CMATH_RECURSION`; after including `<cmath>`, it undefines both ownership macros.

Control flow/dependencies: the control flow is guard, temporary recursion block, standard include, cleanup. It depends only on `<cmath>` and Boost's TR1 recursion convention.

State and persistence: temporary preprocessor state during inclusion. It restores `BOOST_TR1_NO_RECURSION` only when this header set it.

Integration points: standard-library detection headers use `no_tr1` wrappers when probing vendor macros without accidentally including Boost.TR1 replacements.

Risks and test signals: risk is leaking `BOOST_TR1_NO_RECURSION` or recursing when include paths prioritize Boost.TR1. Test by placing Boost.TR1 paths before the standard library and including this wrapper twice.
