# sources/test-tools/fio/t/fuzz/fuzz_parseini.c

## Purpose
libFuzzer entry point that fuzzes fio INI/job-file parsing by feeding arbitrary data into `parse_jobs_ini()` in parse-only mode.

## Important APIs, Types, and Functions
Defines `LLVMFuzzerTestOneInput(const uint8_t *data, size_t size)`. Uses a static `initialized` flag, fake command-line arguments `--output /dev/null --parse-only`, and fio APIs `fio_init_options()`, `parse_cmd_line()`, `sinit()`, and `parse_jobs_ini()`.

## Control Flow
Inputs shorter than two bytes are ignored. The first fuzz call initializes fio option parsing and runtime state. For each input, the harness allocates a buffer, copies all but the last byte, NUL-terminates it, and passes the final input byte as the `stonewall`/type argument to `parse_jobs_ini()`.

## State and Persistence Behavior
Fio initialization is persistent across fuzz cases through static process state. Output is redirected to `/dev/null`; no corpus artifacts are written by the harness itself.

## Dependencies and Integration Points
Links directly against fio parser internals and is meant for libFuzzer or a compatible harness. `onefile.c` in the same directory can drive this entry point with a single file.

## Risks
Process-global fio state may accumulate between fuzz iterations if parser paths are not reentrant or do not fully reset temporary state. The final byte drives parser mode, so generated inputs need at least two bytes to exercise content parsing.

## Test Signals
Crashes, sanitizer findings, leaks, or hangs in `parse_jobs_ini()` are the primary signals. Seed files should include job sections, globals, malformed options, includes, escapes, and truncated lines.
