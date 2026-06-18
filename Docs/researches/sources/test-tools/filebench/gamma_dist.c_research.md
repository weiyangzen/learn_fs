<!-- BEGIN_FILE_RESEARCH: sources/test-tools/filebench/gamma_dist.c -->
# sources/test-tools/filebench/gamma_dist.c

Purpose: samples gamma-distributed random values for Filebench random variables using algorithms from Knuth. It supports the default `drand48()` source or an injected uniform random source plus caller-supplied seed state.

Important APIs/functions: `gamma_dist_knuth(a, b)` uses `drand48()` and returns `b * sample`. `gamma_dist_knuth_src(a, b, src, xi)` does the same with a provided `double (*src)(unsigned short *)`. Internal `gamma_dist_knuth_algG()` handles `0 < a <= 1`; `gamma_dist_knuth_algA()` handles `a > 1`.

Control flow: the public functions branch on `a <= 1.0`. Algorithm G uses rejection sampling with an exponential/power proposal. Algorithm A uses a tangent transform and rejection predicate. Both loop until accepted.

State/persistence: no module state. Default source relies on libc `drand48()` global RNG state; injected source can use `xi`.

Dependencies/integration: depends on `<math.h>` constants/functions and feeds `fb_random`/randdist behavior used by parser-created random variables and `testrandvar` flowop validation.

Risks: there is no validation for `a <= 0`, null `src`, or invalid uniform outputs outside `(0,1)`. Rejection loops can spin for bad parameters or degenerate random sources. `M_E`/`M_PI` availability depends on platform math definitions.

Test signals: distribution tests should compare sample mean/variance for representative `a` values below, equal to, and above one; source-injection tests should use deterministic uniform sequences and invalid-parameter tests should define expected failure behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/filebench/gamma_dist.c -->
