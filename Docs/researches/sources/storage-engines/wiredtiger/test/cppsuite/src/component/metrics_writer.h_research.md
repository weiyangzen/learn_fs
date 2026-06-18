# sources/storage-engines/wiredtiger/test/cppsuite/src/component/metrics_writer.h

Purpose: Declares the singleton metrics writer used for performance JSON generation.

Important APIs/types/functions: `add_stat<T>` accepts arithmetic values only, locks `_stat_mutex`, builds a JSON metric fragment, and appends it. `output_perf_file` writes accumulated metrics.

Control flow: thread-safe appends allow multiple components to save stats before one output pass.

State and persistence: stores stat fragments in `_stats` guarded by a mutex; final file persistence is in the implementation.

Dependencies/integration: included by `metrics_monitor`.

Risks and test signals: no reset API, so multiple tests in one process could share metrics unless process/test runner isolates use. Compile-time `static_assert` catches non-arithmetic metric values.
