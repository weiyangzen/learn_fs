<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-fractal.c -->
# sources/test-tools/stress-ng/stress-fractal.c Research

Purpose: implements `fractal`, a CPU/FP/compute stressor that renders Mandelbrot or Julia rows into a one-row buffer to stress floating-point computation and memory stores without producing an image.

Important APIs/types/functions: `fractal_info_t` stores bounds, step sizes, row buffer, dimensions, and iteration limit. `stress_fractal_method_t` maps method names to row functions and default parameters. `stress_fractal_mandelbrot()` and `stress_fractal_julia()` are optimized target-cloned row renderers with two-column unrolling and residual handling. `stress_fractal_get_row()` coordinates row assignment across instances using an atomic fetch-add when available, or a stress-ng lock fallback.

Control flow: `stress_fractal_init()` creates a shared lock and initializes `g_shared->fractal.row`; deinit destroys it. The stressor reads method, iteration, xsize, and ysize settings; maps a single row buffer; computes `dx/dy`; synchronizes; then repeatedly obtains a row and renders it until stopped. Bogo operations are incremented when row assignment wraps to zero. Metrics report points/sec and fractals/sec.

State and persistence: the only shared state is `g_shared->fractal.row` and its lock. Per-worker row data is an anonymous mapping and is discarded. No rendered image or file persists.

Dependencies and integration: depends on `g_shared` stress-ng shared state, lock helpers, mmap helpers, target clones, sync/state transitions, settings, and metrics. The stressor registers init/deinit callbacks and VERIFY_NONE.

Risks: the atomic row path can produce imperfect wrap behavior when the row counter overflows or when `ysize` does not divide the counter state exactly; the comment accepts this as benchmark noise. Large `xsize` values can request large row buffers. There is no output correctness verification.

Test signals: expected metrics are points/sec and fractals/sec, plus an informational line from instance zero describing method, dimensions, iterations, and complex-plane bounds. Test both methods, lock fallback builds, and extreme size/iteration settings.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-fractal.c -->
