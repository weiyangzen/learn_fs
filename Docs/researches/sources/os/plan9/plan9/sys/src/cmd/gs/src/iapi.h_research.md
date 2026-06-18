# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/iapi.h

Declares the public Ghostscript API and platform export/calling-convention macros. It supports Windows, OS/2, classic Mac export pragmas, and default empty macros for static/non-Windows builds.

API surface:
- revision query
- single-instance create/delete
- stdio, polling, display callbacks
- interpreter initialization
- run string/file helpers
- interpreter exit
- visual tracer debug hook
- function pointer typedefs for dynamic binding

The header explicitly warns that this implementation supports only one Ghostscript instance per process due to global state and `gsapi_instance_counter`.
