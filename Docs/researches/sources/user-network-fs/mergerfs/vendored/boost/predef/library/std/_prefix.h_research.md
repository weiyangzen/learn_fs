<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/library/std/_prefix.h -->
# sources/user-network-fs/mergerfs/vendored/boost/predef/library/std/_prefix.h

## Purpose

`sources/user-network-fs/mergerfs/vendored/boost/predef/library/std/_prefix.h` is the shared prefix header for Boost.Predef C++ standard library detectors. It performs conservative setup before individual library implementation probes run.

## Important APIs, Types, and Functions

Direct includes are `boost/predef/detail/_exception.h`. The file intentionally exposes little or no public macro surface; child detectors define the user-facing `BOOST_LIB_*` macros.

## Control Flow

The include guard prevents duplicate setup. Any conditional include in the prefix runs before implementation-specific headers test vendor library macros, ensuring required standard declarations or feature macros are visible when available.

## State and Persistence Behavior

The header creates no runtime state. Its only persistence is preprocessor include state and any macros made visible by the setup includes.

## Dependencies and Integration Points

It is included by sibling `cloudabi`, `gnu`, `dinkumware`, `libc++`, and similar library detector headers. The prefix keeps common probing assumptions in one place.

## Risks and Edge Cases

Library detection is sensitive to include order and to whether standard headers have already been included. The prefix must stay lightweight so freestanding or partial standard-library environments can still include Boost.Predef.

## Test Signals

Compile the parent library aggregation headers across libstdc++, libc++, MSVC STL, and C runtime variants. Confirm the prefix does not force unavailable standard headers in constrained builds.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/predef/library/std/_prefix.h -->
