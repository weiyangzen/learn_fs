## sources/test-tools/filebench/cvars/mtwist/rdtest.c

### Purpose
`rdtest.c` is the C command-line harness for generating values from `randistrs.c`. It is useful for manual inspection, deterministic sequence checks, and simple statistical pipelines outside the Filebench runtime.

### Important APIs, Types, And Functions
`main` parses `seed`, `count`, `distribution`, and distribution parameters. It calls the default-state `rd_*` APIs such as `rd_iuniform`, `rd_uniform`, `rd_exponential`, `rd_erlang`, `rd_weibull`, `rd_normal`, `rd_lognormal`, `rd_triangular`, `rd_double_empirical`, and `rd_continuous_empirical`. `rd_empirical_setup` prepares empirical controls, while `usage()` prints accepted syntax and exits.

### Control Flow
After parsing input, the program determines the expected number of parameters for the requested distribution. Empirical modes allocate separate `probs` and `values` arrays, reject negative probabilities, and build a control table. If seed is zero it calls `mt_goodseed`; otherwise it calls `mt_seed32`. The generation loop dispatches by string comparison on every iteration and prints one floating-point value per line.

### State And Persistence
The program uses mtwist's default global generator state rather than an explicit `mt_state`. Empirical control state is heap-allocated and not freed before process exit. No persistent files are written.

### Dependencies And Integration Points
It includes `randistrs.h`, `stdio.h`, `stdlib.h`, and `string.h`. It exercises the C API in `randistrs.c` and mtwist default-state seeding. It is the C counterpart to `rdcctest.cc`.

### Risks
Malformed numeric parameters silently parse as zero. Memory allocated for `params`, `probs`, `values`, and empirical controls is not freed. Most distribution parameter domains are not validated beyond Erlang order and empirical nonnegative probabilities. The loop repeatedly compares distribution strings, which is fine for a test harness but not efficient library style.

### Test Signals
Primary test signals are process exit status, stdout sample count, deterministic output for a fixed seed, and compatibility with the C++ harness. Stronger tests should pipe output into statistical checks and cover invalid arguments, all empirical branches, and seed-zero behavior.
