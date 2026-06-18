# sources/distributed-fs/xrootd/python/src/PyXRootDURL.hh

## Purpose
This header defines the Python `URL` binding type.

## Important APIs, Types, and Functions
`class URL` declares accessors/mutators and stores `XrdCl::URL *url`. `URL_init` parses a URL string and allocates `XrdCl::URL`. `URL_dealloc` deletes it. `URL_str` returns the full URL string. `URLGetSet`, `URLMethods`, and `URLType` expose Python properties/methods.

## Control Flow
Object construction requires one string argument. Python property access dispatches to implementations in `PyXRootDURL.cc`. Deallocation frees the C++ URL.

## State and Persistence
The object contains a mutable parsed URL. No persistence.

## Dependencies and Integration Points
Depends on Python C API and `XrdClURL`. Included by conversions, filesystem, module initialization, and URL implementation.

## Risks and Test Signals
Type object is static in a header and must not be duplicated across independent translation units in problematic ways. Tests should verify constructor failures, `str(url)`, property table behavior, and lifecycle.
