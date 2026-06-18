# sources/distributed-fs/xrootd/src/XrdCl/XrdClThirdPartyCopyJob.hh

## Purpose

This header declares the `ThirdPartyCopyJob` concrete `CopyJob` implementation and the state it needs to perform remote-to-remote copies.

## Important APIs, Types, and Functions

The public API is the constructor and `Run(CopyProgressHandler*)`. Private methods are `CanDo`, `RunTPC`, `RunLite`, and `GenerateKey`. Members hold the destination file, source/target URLs, TPC key, checksum configuration, source size, timeout, force/coerce/delegate flags, substream count, and TPC-lite selection.

## Control Flow

The header separates feasibility/probing from execution. `Run` is the external entry point; private methods implement the two copy protocols and key generation.

## State and Persistence Behavior

The object owns an `XrdCl::File dstFile` and value-copy URLs/strings/flags for one job. Results are reported through inherited property/result lists rather than direct persistence.

## Dependencies and Integration Points

It includes copy-process, copy-job, and file interfaces. The job is created directly by copy orchestration or by `TPFallBackCopyJob`.

## Risks and Edge Cases

Because the class stores mutable per-run state, a single instance should not be reused concurrently. Header consumers need the implementation to close `dstFile` in all error paths.

## Test Signals

Compile/link coverage plus the behavior tests for the `.cc` file validate this declaration.
