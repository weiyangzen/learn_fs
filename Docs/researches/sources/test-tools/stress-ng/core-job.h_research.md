# sources/test-tools/stress-ng/core-job.h

## Purpose

This header declares the stress-ng job-file parser entry point.

## Important APIs, Types, And Functions

It exposes `stress_job_parse_file(const int argc, char **argv, const char *jobfile)`.

## Control Flow

Callers invoke the parser during option processing. Passing `NULL` for `jobfile` allows the implementation to consume the next command-line argument as a job file.

## State And Persistence Behavior

The implementation can update global option state and `optind`. The header owns no state.

## Dependencies And Integration Points

The parser integrates with command-line option handling and job scripts.

## Risks And Test Signals

Signature stability is the main concern. Tests should cover `NULL` and explicit jobfile modes.
