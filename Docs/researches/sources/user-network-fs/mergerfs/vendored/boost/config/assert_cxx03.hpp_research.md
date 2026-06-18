<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/assert_cxx03.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/config/assert_cxx03.hpp

## Purpose
This generated Boost.Config assertion header fails compilation if the active compiler/stdlib configuration reports missing C++03 conformance features.

## Important APIs, Types, And Control Flow
It includes `boost/config.hpp`, then checks a long list of `BOOST_NO_*` defect macros such as ADL barriers, argument-dependent lookup, cv specializations, exceptions, function template ordering, `long long`, member templates, SFINAE, standard namespace/library facilities, template partial specialization, two-phase lookup, RTTI, and type traits-related support. Each detected defect produces a targeted `#error` naming the macro.

## State And Persistence
There is no runtime state. Its only output is a compile success or a preprocessing error.

## Dependencies And Integration Points
It depends on the entire Boost.Config selection stack to have defined accurate defect macros. It integrates as a validation include for builds that require C++03 support from the current toolchain.

## Risks And Test Signals
Risks include stale or overly conservative compiler configs causing false failures, or user configs masking defect macros. Test signals are compile-only checks under supported compilers and deliberate `-D BOOST_NO_*` injections to confirm the expected `#error` path.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/assert_cxx03.hpp -->
