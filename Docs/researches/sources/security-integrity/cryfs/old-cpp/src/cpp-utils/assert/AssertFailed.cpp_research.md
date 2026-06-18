# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/assert/AssertFailed.cpp

## Purpose
Implements the cpp-utils assertion failure model, crash backtrace hooks, and thread-local controls used throughout CryFS to convert invariant failures into logs, exceptions, or aborts. This specific file has 2 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/assert` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Primary includes/dependencies visible in the file include `AssertFailed.h`.

## Control Flow
Assertion paths format file/line/expression context, log the failure, optionally throw `AssertFailed` instead of aborting while the RAII disable counter is active, and crash handlers log platform backtraces before exiting.

## State and Persistence Behavior
State is process-local: assertion abort-disable counters are thread-aware/global in the assertion header, while signal/backtrace registration modifies process signal handling.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are `AssertFailed.h`.

## Risks and Edge Cases
Assertion behavior changes process failure mode. Throw-vs-abort counters must be balanced and crash signal handlers must avoid unsafe work beyond logging/exiting.

## Test Signals
Assertion tests should cover throw mode, abort/log formatting in safe harnesses, RAII counter balance, and crash-backtrace registration on each platform.

## File-Specific Notes
- This file is intentionally tiny; its main role is to provide the translation unit or include anchor for inline/template definitions in the paired header.
