# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/ttfmemd.h

Header declaring TrueType GC structure descriptors.

Key points:
- Includes `gsstype.h`.
- Declares external structure descriptors:
  - `st_TFace`
  - `st_TInstance`
  - `st_TExecution_Context`
  - `st_ttfFont`
  - `st_ttfInterpreter`

Dependencies and interactions:
- Included by code that allocates these structures with Ghostscript’s typed allocator.

Research relevance:
- Descriptor declaration header for GC-aware TrueType object allocation.
