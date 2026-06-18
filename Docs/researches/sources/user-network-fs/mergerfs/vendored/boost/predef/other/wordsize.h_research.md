# sources/user-network-fs/mergerfs/vendored/boost/predef/other/wordsize.h

Purpose: Derives the native architecture word size in bits from Boost.Predef architecture headers.

Important APIs, types, and functions: Defines `BOOST_ARCH_WORD_BITS` as `64`, `32`, `16`, or `0`, plus `BOOST_ARCH_WORD_BITS_64`, `BOOST_ARCH_WORD_BITS_32`, `BOOST_ARCH_WORD_BITS_16`, and name macros.

Control flow: The header includes `boost/predef/architecture.h`, then checks whether architecture-specific headers already defined a `BOOST_ARCH_WORD_BITS_*` macro. The first available size in the order 64, 32, 16 sets `BOOST_ARCH_WORD_BITS`; missing indicator macros are explicitly defaulted to not available.

State and persistence behavior: Compile-time-only; no runtime state or storage. It produces a single numeric macro usable in preprocessor and compiler expressions.

Dependencies and integration points: Pulls all architecture detection headers, so it can be used by platform code requiring coarse data model decisions.

Risks: Word size is manually maintained in architecture detectors and may be unavailable for newer or uncommon architectures, leaving `BOOST_ARCH_WORD_BITS` as `0`. It should not be treated as pointer width on exotic ABIs without checking platform documentation.

Test signals: Test declarations cover the aggregate word-bit macro and each size-specific indicator.
