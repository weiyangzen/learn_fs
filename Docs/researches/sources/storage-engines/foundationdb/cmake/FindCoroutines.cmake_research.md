# sources/storage-engines/foundationdb/cmake/FindCoroutines.cmake

## Purpose
Detects C++ coroutine header/library support and creates an imported target for consumers.

## Important APIs, Types, and Functions
Defines result variables `CXX_COROUTINES_HAVE_COROUTINES`, `CXX_COROUTINES_HEADER`, `CXX_COROUTINES_NAMESPACE`, `Coroutines_FOUND`, and imported target `std::coroutines`.

## Control Flow and Integration
The module probes compiler flags (`/await`, `-fcoroutines-ts`, `-fcoroutines`), normalizes requested components (`Final`, `Experimental`), checks headers and compilation snippets, then builds an interface target with extra compile options if needed.

## State and Persistence
Depends on CMake check modules and compiler support for C++17/C++20 coroutine syntax.

## Dependencies
State is cached in CMake variables and target properties.

## Risks and Test Signals
Risks include old TS/final coroutine ambiguity, flag checks passing but target code failing, and stale cached results after compiler changes. Test signal is successful compilation of the embedded coroutine factorial snippet.
