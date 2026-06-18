# sources/user-network-fs/mergerfs/vendored/boost/predef/version_number.h

Purpose: Defines Boost.Predef's compact numeric version encoding and extraction macros.

Important APIs, types, and functions: Public macros are `BOOST_VERSION_NUMBER(major, minor, patch)`, `BOOST_VERSION_NUMBER_MAX`, `BOOST_VERSION_NUMBER_ZERO`, `BOOST_VERSION_NUMBER_MIN`, `BOOST_VERSION_NUMBER_AVAILABLE`, `BOOST_VERSION_NUMBER_NOT_AVAILABLE`, and `BOOST_VERSION_NUMBER_MAJOR/MINOR/PATCH`.

Control flow: Macro arithmetic encodes a two-digit major, two-digit minor, and five-digit patch as `MMmmppppp`; inputs are modulo-truncated to their supported ranges.

State and persistence behavior: No runtime state. This file underpins nearly every Boost.Predef detection macro.

Dependencies and integration points: Standalone include used by OS, platform, architecture, library, and workaround detectors.

Risks: Values outside documented ranges are silently modulo-truncated. Callers needing semantic-version precision beyond two/two/five digits cannot use this representation directly.

Test signals: No direct generated test declaration, but all detector tests depend on these constants.
