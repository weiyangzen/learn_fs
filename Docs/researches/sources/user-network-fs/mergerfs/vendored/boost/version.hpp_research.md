# sources/user-network-fs/mergerfs/vendored/boost/version.hpp

## Purpose

This Boost configuration header records the vendored Boost release version. It is the canonical Boost header expected to change on every Boost release and is used by client code and Boost auto-link logic.

## Important APIs, types, and functions

`BOOST_VERSION` is defined as `109000`, encoding major, minor, and patch as `major * 100000 + minor * 100 + patch`. That value corresponds to Boost 1.90.0.

`BOOST_LIB_VERSION` is defined as the string `"1_90"`, the form used by Boost auto-link configuration to select versioned library names.

## Control Flow

There is no runtime or compile-time branching beyond the include guard. The comments document how to decode the numeric macro.

## State and Persistence Behavior

The header defines version macros only. It stores no runtime state. Because many files may include it, changing it intentionally causes broad recompilation.

## Dependencies and Integration Points

It has no includes. It integrates with Boost.Config documentation, feature checks, build scripts, and auto-link selection via `config/auto_link.hpp` in environments that use Boost's library naming conventions.

## Risks and Edge Cases

The macros must match the actual vendored Boost tree. A mismatch can confuse conditional compilation, diagnostics, package reporting, or auto-link library selection. Since this repository vendors selected Boost headers, consumers may assume more Boost components at version 1.90 than are actually present.

## Test Signals

Build metadata checks should confirm `BOOST_VERSION == 109000` and `BOOST_LIB_VERSION == "1_90"` match the vendored source snapshot. Downstream compile tests can include this header alone and verify version-gated code paths select expected Boost 1.90 behavior.
