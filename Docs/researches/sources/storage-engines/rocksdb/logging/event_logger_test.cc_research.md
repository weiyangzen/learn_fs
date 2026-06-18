# sources/storage-engines/rocksdb/logging/event_logger_test.cc

Purpose: Minimal test for `EventLogger` structured output.

Important APIs/types/functions: `StringLogger`, `EventLogger`, `event_logger.Log() << key << value`.

Control flow and state: `StringLogger` captures the most recent formatted log line in a fixed buffer. The test writes an event with `id` and `event`, then asserts the captured output contains those fields and `time_micros`.

State and persistence behavior: all output is in memory; no files.

Dependencies and integration points: tests the generic `Logger` interface and event stream destructor emission.

Risks: only substring checks are performed; JSON validity, prefix presence, escaping, arrays, and buffer logging are not covered.

Test signals: smoke signal that stream insertion emits fields on destruction.
