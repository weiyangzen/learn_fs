## sources/test-tools/filebench/cvars/mtwist/rdcctest.cc

### Purpose
`rdcctest.cc` is a C++ command-line generator for manually exercising the random distribution library. It parses a seed, a count, a distribution name, and distribution parameters, then prints generated values to stdout using the C++ mtwist distribution wrappers.

### Important APIs, Types, And Functions
The only public entry point is `main`. It uses `mt_distribution` for PRNG/distribution generation and conditionally allocates an `mt_empirical_distribution` for empirical cases. `usage()` prints accepted distributions and exits with status 2. Supported distribution names include `iuniform`, `uniform`, `exponential`, `erlang`, `weibull`, `normal`, `lognormal`, `triangular`, `empirical`, and `continuous_empirical`.

### Control Flow
The program validates a minimum argument count, parses numeric parameters into a dynamically allocated `double` array, then branches by distribution name to determine required parameter count. Empirical modes build `std::vector<double>` values and probabilities, reject negative probabilities, and create an `mt_empirical_distribution`. A generator is constructed with automatic seeding when the seed argument is zero; otherwise `seed32(seed)` fixes deterministic output. The main loop dispatches to the selected distribution and writes one value per line.

### State And Persistence
State is in the local `mt_distribution distr` object and, for empirical runs, a heap-allocated `mt_empirical_distribution`. No files or persistent state are written. A fixed nonzero seed provides reproducibility; seed zero delegates seed selection to mtwist.

### Dependencies And Integration Points
It includes `randistrs.h`, `iostream`, `stdlib.h`, `string.h`, and `vector`. It validates the C++ wrapper interface in `randistrs.h` and indirectly exercises `randistrs.c` plus `mtwist.c`.

### Risks
The code allocates `params` with `new[]` and empirical objects with `new` but never deletes them; acceptable for a short test program but not clean. `usage()` prints a stale syntax line missing the seed parameter even though `main` expects it. Numeric parsing uses `atoi`/`atof`, so malformed strings silently become zero. There is no statistical assertion; this is an output generator, not an automated correctness test.

### Test Signals
Useful signals are successful compilation as C++, expected failure on bad parameter counts and negative empirical weights, deterministic output for fixed seeds, and parity against `rdtest.c` for equivalent distributions and seeds.
