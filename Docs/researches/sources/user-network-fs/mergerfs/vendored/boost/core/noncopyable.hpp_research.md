# sources/user-network-fs/mergerfs/vendored/boost/core/noncopyable.hpp

Purpose: Defines `boost::noncopyable`, a base class that disables copy construction and copy assignment.

Important APIs, types, and functions: `boost::noncopyable` and implementation namespace `boost::noncopyable_::noncopyable`.

Control flow: No runtime flow; copy operations are deleted in modern compilers or private/unimplemented in older compilers.

State and persistence behavior: Empty base type with no state.

Dependencies and integration points: Used by classes that need noncopyable semantics without including heavier Boost headers.

Risks: Inheritance affects type traits and aggregate behavior; old compiler private declarations produce different diagnostics than deleted functions.

Test signals: Static assertions or compile-fail checks for copy construction/assignment and size/EBO behavior when used as a base.
