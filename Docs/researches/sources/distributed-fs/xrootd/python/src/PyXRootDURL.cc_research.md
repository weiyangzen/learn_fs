# sources/distributed-fs/xrootd/python/src/PyXRootDURL.cc

## Purpose
This source implements property accessors and methods for the Python `URL` object wrapping `XrdCl::URL`.

## Important APIs, Types, and Functions
Methods include `IsValid` and `Clear`. Getters/setters cover `hostid`, `protocol`, `username`, `password`, `hostname`, `port`, `path`, and read-only `path_with_params`.

## Control Flow
Getters pull string or integer fields from the underlying XrdCl URL and return Python values. Setters validate Python type (`str` or `int`), convert to C++ strings or long, update the XrdCl URL, and return 0 or -1 with a Python exception. `Clear` resets the URL object and returns `None`.

## State and Persistence
All state is the mutable in-memory `XrdCl::URL` owned by the Python object. No persistent side effects.

## Dependencies and Integration Points
Depends on `PyXRootDURL.hh` and XrdCl URL semantics. Used directly by Python users and by host-list conversion and filesystem construction.

## Risks and Test Signals
Setters do not check `PyUnicode_AsUTF8` or `PyLong_AsLong` error conditions beyond initial type checks. URLs with invalid port ranges depend on XrdCl handling. Tests should cover construction, stringification, validation, every getter/setter, invalid setter types, clearing, and filesystem use of a URL-derived host.
