# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/632

## Purpose
This fixture validates a corrupted KMSAN uninitialized-value report in `__perf_event_task_sched_in`.

## Important APIs, types, and functions
Key symbols include `__perf_event_task_sched_in`, `stack_depot_fetch`, `kmsan_print_origin`, `kmsan_report`, and `__msan_warning`.

## Control flow
During scheduler/perf event task switch handling, KMSAN detects uninitialized data. Origin reporting itself warns because stack depot data is out of bounds, so the fixture is marked corrupted.

## State and persistence behavior
The persisted state includes `CORRUPTED: Y`, KMSAN type, warning side-effect, and partial origin data.

## Dependencies and integration points
It tests KMSAN parsing, perf/scheduler attribution, and corruption handling when sanitizer origin metadata is damaged.

## Risks and test signals
The parser must preserve the KMSAN title while acknowledging corruption, rather than switching to `stack_depot_fetch`.
