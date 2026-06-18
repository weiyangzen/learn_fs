# sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/0

## Purpose

This OpenBSD fixture expects title `uvm_fault` and marks the report `CORRUPTED: Y`. It is a short page-fault transcript ending at `vn_writechk+0x13`, used to verify that a damaged or incomplete crash log can still be recognized while being flagged as corrupted.

## Important APIs, Types, and Functions

Reporter-facing items are `TITLE:`, `CORRUPTED: Y`, page-fault matching, and DDB stop-line parsing. Kernel evidence includes `uvm_fault(...) -> e`, `kernel: page fault trap, code=0`, and `Stopped at vn_writechk+0x13`.

## Control Flow

The log begins around a login prompt, reports a UVM fault, then stops at an instruction in `vn_writechk`. There is no trace, process table, or DDB command output. The parser should prefer the generic `uvm_fault` title because the report is explicitly corrupted and too incomplete to form a reliable function-specific title.

## State and Persistence Behavior

The fixture persists only the fault map/address/code tuple and a stopped instruction. Parser state should record the corruption annotation separately from crash title selection. Address values and the stopped instruction are volatile evidence.

## Dependencies and Integration Points

This integrates OpenBSD page-fault detection with corrupted-report metadata handling. It protects callers that need to keep crash evidence while reducing confidence in deduplication or reproduction signals.

## Risks and Edge Cases

The main risk is over-trusting an incomplete stop frame and producing a specific title such as `uvm_fault in vn_writechk`. Another risk is discarding the crash entirely because the trace is absent. The CR-style carriage returns in the source also test console text normalization.

## Test Signals

A passing test returns `uvm_fault`, marks the parsed report as corrupted, and includes the `kernel: page fault trap` and `vn_writechk` stop line in the body.
