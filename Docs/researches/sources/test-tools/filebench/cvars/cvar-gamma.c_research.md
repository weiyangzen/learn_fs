<!-- BEGIN_FILE_RESEARCH: sources/test-tools/filebench/cvars/cvar-gamma.c -->
# `sources/test-tools/filebench/cvars/cvar-gamma.c`

Purpose: Standalone gamma-distribution CVAR plugin using Knuth algorithms from original Filebench distribution code.

Important APIs/functions: CVAR entry points plus private `gamma_dist_knuth_algG` for `0 < a <= 1`, `gamma_dist_knuth_algA` for `a > 1`, `default_src`, `gamma_dist_knuth`, and `gamma_dist_knuth_src`. Parameters are `mean` and `gamma`; handle stores `mean`, `scaledmean`, and `gamma`.

Control flow: allocation tokenizes parameters, reads `mean` and `gamma`, rejects only `gamma == 0`, computes `scaledmean = mean / gamma`, rejects unknown tokens, and allocates the handle. Sampling validates pointers and calls `gamma_dist_knuth(h->gamma, h->scaledmean)`, which selects algorithm G or A and uses rejection loops driven by `drand48()`.

State and persistence: unlike other CVAR modules, no RNG state is stored in the handle. Randomness comes from process-global `drand48()` state. `cvar_revalidate_handle` is a no-op.

Dependencies and integration: includes standard `math.h`, `stdlib.h`, CVAR ABI, trace, and tokenizer. Built as `libcvar-gamma.la`; linked with the common MT sources by `Makefile.am` even though this file does not call them.

Risks: global `drand48()` is not per-handle, not explicitly seeded here, and may be non-reentrant or platform-limited. Negative `gamma` is accepted and can route into formulas whose documented domain is positive. Negative/zero mean is not validated. `gamma_dist_knuth_src` is unused in this plugin. `atof` parsing is weak.

Test signals: default sampling, explicit positive mean/gamma, `gamma:0` rejection, negative gamma/mean edge cases, reproducibility under controlled `srand48`, and concurrent handles sharing global RNG state.
<!-- END_FILE_RESEARCH: sources/test-tools/filebench/cvars/cvar-gamma.c -->
