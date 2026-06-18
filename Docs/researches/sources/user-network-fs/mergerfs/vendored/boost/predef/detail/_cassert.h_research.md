<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/detail/_cassert.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/detail/_cassert.h

## Purpose

`sources/user-network-fs/mergerfs/vendored/boost/predef/detail/_cassert.h` is a Boost.Predef detail header for assert configuration shim. It conditionally includes `<assert.h>` only when predef tests are enabled and `NDEBUG` is not set.

## Important APIs, Types, and Functions

The exposed preprocessor surface is none. Direct includes are `cassert`, `assert.h`. These names are implementation support for other Predef headers, not end-user feature tests.

## Control Flow

The include guard protects the shim. Depending on the file, it either defines a sentinel macro immediately, conditionally includes a standard header, or defines no-op/self-test macros used by detector headers after their main include guard closes.

## State and Persistence Behavior

No runtime state is created. Sentinel macros persist only within the current preprocessing translation unit and influence later included Predef headers.

## Dependencies and Integration Points

This file is included by compiler, OS, platform, library, or test-registration headers in the same vendored Boost.Predef tree. Its integration role is ordering and configuration support for the generated `BOOST_*` detection macros.

## Risks and Edge Cases

Although tiny, these files are order-sensitive. If a detected sentinel is defined too early or omitted, later detectors can report primary versus emulated availability incorrectly. Conditional standard-header inclusion must stay conservative for freestanding or unusual compiler modes.

## Test Signals

Preprocessor tests should include the relevant parent detector families and assert that sentinels or no-op test macros are defined exactly as expected. Cross-compilation jobs are useful because these detail shims are most visible in unusual target environments.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/detail/_cassert.h -->
