# sources/distributed-fs/xrootd/src/XrdCl/XrdClTPFallBackCopyJob.hh

## Purpose

This header declares the fallback copy job type used when copy configuration wants to try third-party copy before streaming.

## Important APIs, Types, and Functions

`TPFallBackCopyJob` derives from `CopyJob`. It exposes a constructor accepting job ID, properties, and results; a virtual destructor; and `Run(CopyProgressHandler*)`. The only member is the owned delegate `CopyJob *pJob`.

## Control Flow

The header establishes the polymorphic `CopyJob` contract. Implementation code chooses the concrete delegate at runtime and forwards `Run` calls.

## State and Persistence Behavior

State is limited to an owned delegate pointer. Job properties/results are non-owned pointers inherited from `CopyJob`.

## Dependencies and Integration Points

It includes copy-process and copy-job interfaces. Copy orchestration code can treat this class as a normal `CopyJob`.

## Risks and Edge Cases

The raw pointer requires destructor and replacement code to remain exception-safe and avoid leaks. The class is not copy-safe and does not declare deleted copy operations.

## Test Signals

Compile/link tests plus runtime fallback tests in the `.cc` file are the main signals.
