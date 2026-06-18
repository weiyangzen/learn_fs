# sources/test-tools/stress-ng/core-put.h

Purpose: exposes tiny inline sinks that write values into global `g_put_val` so optimized stress loops can make computed values observable to the compiler. This prevents whole-loop dead-code elimination without introducing heavy I/O.

Important APIs/types/functions: `g_put_val` is the external sink object. `stress_put_bool`, integer width variants, optional `stress_put_uint128`, floating-point variants, and `stress_put_void_ptr` store the supplied value into the matching union/struct member.

Control flow: every helper is an `ALWAYS_INLINE` single assignment. The only conditional path is `HAVE_INT128_T`, which enables the 128-bit sink when supported.

State and persistence: all functions mutate the process-global `g_put_val`. The value is intentionally overwritten and not accumulated. There is no synchronization, so concurrent writers race by design as a compiler-observability sink rather than a correctness store.

Dependencies/integration: included by hot stressor code and relies on the definition of `stress_put_val_t` elsewhere in stress-ng. It integrates with benchmark loops where returning or printing values would distort the workload.

Risks: strict type matching matters because the helpers directly assign to typed members. Thread sanitizer-style tools may flag benign global data races. If `g_put_val` is removed or made local, optimizer behavior of many stressors can change.

Test signals: optimized builds should still retain loops that call these helpers. Compile with and without `__int128` support.
