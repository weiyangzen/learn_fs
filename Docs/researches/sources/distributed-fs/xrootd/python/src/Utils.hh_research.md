# sources/distributed-fs/xrootd/python/src/Utils.hh

## Purpose
This header declares utility helpers shared by the PyXRootD extension.

## Important APIs, Types, and Functions
It declares `IsCallable`, `InitTypes`, and numeric conversion helpers for unsigned long, unsigned int, unsigned short, and unsigned long long values.

## Control Flow
No implementations are present; it provides prototypes for source files that need argument validation and callback handling.

## State and Persistence
No state or persistence in the header.

## Dependencies and Integration Points
Depends on `PyXRootD.hh` and XrdCl response headers. Included by file, async, conversions, and other binding components.

## Risks and Test Signals
Header risk is declaration/implementation drift. Build tests cover signatures; runtime tests cover behavior in `Utils.cc`.
