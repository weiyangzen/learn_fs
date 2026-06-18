## sources/test-tools/filebench/fb_random.h

### Purpose
`fb_random.h` declares Filebench random helper APIs and defines the structures used for random distribution variables in workload definitions.

### Important APIs, Types, And Functions
`probtabent_t` represents parsed probability table segments. `randfunc_t` is a normalized lookup-table entry with base and range. `randdist_t` stores distribution function pointers, source function pointers, AVD parameters, resolved double/integer values, table entries, lookup table, `erand48` seed words, and type flags. Public functions are `fb_random64`, `fb_random32`, `randdist_alloc`, and `randdist_init`.

### Control Flow
The header establishes the initialization model: parser code fills a `randdist_t` with type/source/parameter AVDs and optional probability table entries, then calls `randdist_init` to resolve function pointers and numeric tables before values are generated through `rnd_get`.

### State And Persistence
`randdist_t` objects are linked through `rnd_next` and commonly allocated in shared memory. They store both declarative AVD pointers and resolved values, so they are mutable initialization products rather than immutable specifications.

### Dependencies And Integration Points
It includes `filebench.h` for `avd_t`, `fbint_t`, and shared runtime types. `vars.c` and parser code use these structures to represent random variables; `fb_random.c` implements the declared behavior.

### Risks
The function-pointer fields require successful initialization before use. `PF_TAB_SIZE` is fixed at 100, so probability table percentages are expected to map to integer slots. Type/source flags share `rnd_type` bits, so masks must be used correctly. No ownership comments are provided for `probtabent_t` chains.

### Test Signals
Compile tests should validate consumers can allocate and initialize all distribution types. Runtime tests should inspect `rnd_get`, `rnd_src`, `rnd_rft`, and resolved fields after `randdist_init` for uniform, gamma, table, mtwist, and generator source modes.
