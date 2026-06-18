<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/compiler/common_edg.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/config/compiler/common_edg.hpp

## Purpose
This shared adapter defines Boost.Config defaults for EDG-front-end compilers.

## Important APIs, Types, And Control Flow
It requires `__EDG_VERSION__`, then defines defects for older EDG versions: missing int64, SFINAE, void returns, ADL, template templates, abstract detection, and function-scope using declaration ADL issues. It detects exception and long-long support, enables pragma once, and defines broad C++11 feature absences with SD-6 based exceptions for char types, Unicode literals, user literals, variadic templates, constexpr, lambdas, range-for, raw strings, C++14, and C++17 features.

## State And Persistence
All state is preprocessor-only. No functions or objects are emitted.

## Dependencies And Integration Points
It is included by Comeau, Intel fallback, Cray, and other EDG-derived compiler configs. It provides a conservative baseline that those compiler-specific files may refine or override.

## Risks And Test Signals
Risks include over-disabling features for newer EDG-based compilers and exception detection differences for KAI. Test signals are Boost.Config feature-check compilations before and after compiler-specific overrides, especially C++11/C++14 SD-6 gates.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/compiler/common_edg.hpp -->
