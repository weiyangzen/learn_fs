## sources/test-tools/stress-ng/stress-vecfp.c

Purpose: Implements `vecfp`, a selectable floating-point vector arithmetic throughput stressor.

Important APIs/types/functions: `stress_vecfp_info`, generated add/mul/div/neg functions, `stress_vecfp_call_method`, `stress_vecfp_all`, `stress_vecfp_method`, and `stress_vecfp`; option `vecfp-method` selects all or a specific float/double width/operator.

Control flow: allocates initialization records for the maximum vector width, fills deterministic random initial/add/multiply/reverse values, and repeatedly calls the selected vector method. Each method runs `LOOPS_PER_CALL` arithmetic on vector types and stores results. Optional verification reruns into a second result slot and compares float/double tolerances.

State and persistence: per-method static metrics accumulate duration/count; init data is anonymous mmap and freed on exit.

Dependencies/integration: compiler vector extensions, target clones, SIGILL catching, `core-mmap`, stress-ng method option parsing, and metric reporting.

Risks: floating point tolerance is fixed and may be sensitive to compiler optimization, FMA, precision, or target-specific math; huge vector types require compiler support.

Test signals: `VERIFY_OPTIONAL`; emits per-method Mfp-ops/sec and reports result mismatches when verify is active.
