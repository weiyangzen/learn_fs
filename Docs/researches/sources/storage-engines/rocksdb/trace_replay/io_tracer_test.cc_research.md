# sources/storage-engines/rocksdb/trace_replay/io_tracer_test.cc

## Purpose

Unit tests for IO trace writer, reader, and controller lifecycle.

## Important APIs, Control Flow, And Dependencies

The fixture creates a temporary trace file and helper functions to generate file operation names, write repeated records with length/offset bits, and verify decoded records. Tests cover multiple optional field combinations, request ID through `IODebugContext`, one-record atomic write, write before start, no write after end, and direct writer multiple-record output.

## State, Persistence, Integration, Risks, And Test Signals

Each test writes a trace file and reads it back through `IOTraceReader`, checking header version fields and decoded record data. Required state includes temporary directories and `TraceWriter`/`TraceReader` file objects. The tests assert that optional fields not present in `io_op_data` remain default zero and that missing records produce non-OK reads. Risks are limited coverage for corrupted payloads and unknown bit values, but the suite confirms the normal binary contract and controller start/stop behavior.
