# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/note.h

## Purpose

`note.h` provides the low-level `_NOTE()` annotation macro used throughout exported and kernel headers to embed source annotations for external tools without polluting user namespace with the preferred public `NOTE` macro.

## Main Interfaces

If `_NOTE` is not already defined, the header defines `_NOTE(s)` as an empty macro. Tooling can interpose a different `sys/note.h` implementation that expands annotations for static analysis or documentation.

## Runtime Use

There is no runtime behavior. In normal builds, annotations compile away completely.

## Dependencies

The file is self-contained and includes only C++ linkage guards.

## Risks and Invariants

Exported headers should use `_NOTE` rather than `NOTE` to avoid stealing names from consumers. Tool interposition relies on `_NOTE` being consistently used and normally inert.
