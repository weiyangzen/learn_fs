## sources/test-tools/filebench/cvars/mtwist/randistrs.h

### Purpose
`randistrs.h` declares the mtwist-based random distribution API for C and C++ consumers. It documents the three access styles: `rds_*` functions using caller-provided `mt_state`, `rd_*` functions using the default mtwist state, and C++ `mt_distribution`/`mt_empirical_distribution` wrappers.

### Important APIs, Types, And Functions
The key exported control type is `rd_empirical_control`, which stores the alias-table data used by empirical distributions: `n`, `cutoff`, `remap`, and `values`. The header declares all state-based distribution functions, all default-state wrappers, and `rd_empirical_setup`/`rd_empirical_free`. Under C++, `mt_distribution` derives from `mt_prng` and forwards methods like `uniform`, `normal`, and `triangular` to the C functions. `mt_empirical_distribution` owns an `rd_empirical_control *` and exposes empirical generation methods taking an `mt_prng &`.

### Control Flow
The header itself does not implement C control flow, but it fixes the calling patterns for `randistrs.c`: initialize or zero an `mt_state`, call a distribution function, and optionally reuse empirical control tables across independent generators. In C++, constructors initialize the underlying `mt_prng`; distribution methods forward through the protected state object.

### State And Persistence
Distribution calls are stateless except for the PRNG state and empirical control allocations. The header explicitly recommends the `rds_*` stateful interface for serious uses because independent streams reduce accidental correlation. `mt_empirical_distribution` manages the control lifetime with RAII but forbids copying and assignment.

### Dependencies And Integration Points
The header includes `mtwist.h` and, for C++, `stdexcept` and `vector`. It is included by `randistrs.c`, `rdtest.c`, and `rdcctest.cc`, and can be used by custom variable libraries that need mtwist distributions.

### Risks
The documented empirical `values` contract is easy to misuse: even discrete double empirical setup copies `n_probs + 1` values if `values` is non-null. The C++ empirical wrapper assumes C `malloc/free` interoperate safely in the runtime used by C++ object construction/destruction. The header exposes raw pointers and does not encode parameter constraints in types.

### Test Signals
Compile tests should cover both C and C++ inclusion. Runtime tests should verify that `rd_*` and `rds_*` produce equivalent sequences when given equivalent default and explicit states, that the C++ wrappers match the C functions, and that empirical construction rejects mismatched vector sizes in C++.
