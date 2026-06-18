<!-- BEGIN_FILE_RESEARCH: sources/test-tools/filebench/gamma_dist.h -->
# sources/test-tools/filebench/gamma_dist.h

Purpose: declares the gamma random sampling interface used by Filebench random distribution code.

Important APIs: `gamma_dist_knuth(double a, double b)` samples using the default libc generator. `gamma_dist_knuth_src(double a, double b, double (*src)(unsigned short *), unsigned short *xi)` lets callers provide a random source compatible with seed arrays.

Control flow contract: callers supply gamma shape `a` and multiplier `b`; the implementation chooses the correct Knuth algorithm by shape.

State/persistence: the header declares stateless functions, but the default implementation depends on global `drand48()` state.

Dependencies/integration: includes `filebench.h` for project context and is expected by random variable machinery.

Risks: no documented preconditions in the header beyond implementation comments; callers must know that `a` must be positive and source functions must return valid uniform doubles.

Test signals: compile checks for random distribution modules and WML `randvar` gamma tests that verify repeatability when seeded through the injected source path.
<!-- END_FILE_RESEARCH: sources/test-tools/filebench/gamma_dist.h -->
