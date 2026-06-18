<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-funcret.c -->
# sources/test-tools/stress-ng/stress-funcret.c Research

Purpose: implements `funcret`, a CPU stressor that exercises function return value copying and ABI return paths for small integers, floating types, optional extended types, and large structs.

Important APIs/types/functions: macros generate one-level, deep, and deeper return wrappers for each type. `stress_funcret_type()` generates per-type tests that initialize a value, pass it through generated return wrappers 1000 times, and verify that returned values remain stable. `stress_funcret_setvar()` randomizes object bytes. `stress_funcret_methods[]` maps method names to functions, including large `stress_uint8x32_t`, `stress_uint8x128_t`, and `stress_uint64x128_t` structures. `stress_funcret_exercise()` records timing and logs verification failures.

Control flow: `stress_funcret()` reads `funcret-method`, zeros metrics, synchronizes, and repeatedly exercises the selected method or `all` until failure or stop. On completion it emits per-method invocation-rate metrics and returns success only if verification never failed.

State and persistence: static metrics are process-local and reset per run. Test variables are stack-local. Generated wrappers intentionally copy through temporaries and clear inputs to force real return copying. No persistent state exists.

Dependencies and integration: uses stress-ng random bytes, memory shims, metrics, sync/state, method option parsing, and architecture/compiler feature macros. s390 decimal support is guarded by project pragmas; clang-disabled paths avoid unsupported decimal/extended return handling.

Risks: optional type coverage changes significantly by compiler and architecture. Floating comparison casts to double and uses tolerance, which is pragmatic but can miss some extended precision issues. The option key in `opts` is `"funcret_method"` while help advertises `funcret-method`; that mismatch is a potential CLI integration issue unless normalized elsewhere.

Test signals: failures report the selected function return method. Expected metrics are per-type function invocations/sec. Test with all compiled methods, selected large-struct methods, and compiler variants for decimal and extended FP returns.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-funcret.c -->
