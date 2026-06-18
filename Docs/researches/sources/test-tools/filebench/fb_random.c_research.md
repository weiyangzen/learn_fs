## sources/test-tools/filebench/fb_random.c

### Purpose
`fb_random.c` provides Filebench random number helpers and random-distribution objects. It can draw raw random values from mtwist or an `avd_t` random variable, apply max/round constraints, and initialize distribution objects for uniform, gamma, or table-driven workload parameters.

### Important APIs, Types, And Functions
Public APIs are `fb_random64`, `fb_random32`, `randdist_alloc`, and `randdist_init`. Internal helpers include `fb_random_probability`, `fb_rand_src_rand48`, `fb_rand_src_random`, `rand_uniform_get`, `rand_gamma_get`, `rand_table_get`, and `rand_seed_set`. Distribution objects are `randdist_t` from `fb_random.h`.

### Control Flow
`fb_random64` either obtains a value from an `avd_t` random variable or calls `mt_llrand`, normalizes it to `[0,max]`, subtracts `round` from `max` to keep later I/O ranges safe, and rounds down to a multiple when requested. `fb_random32` delegates to the 64-bit path and casts. `randdist_alloc` allocates a shared-memory distribution and links it into `shm_rand_list`. `randdist_init` resolves AVD parameters, selects the generation function by `rnd_type`, chooses either `erand48` seeded from `rnd_seed` or Filebench's mtwist source, and converts any probability table into a 100-slot normalized lookup table.

### State And Persistence
Random distribution definitions live in shared memory through `filebench_shm->shm_rand_list`. Each distribution stores resolved means, gamma, min, round, random source state (`rnd_xi`), and function pointers. The mtwist default state is external global state. No persistent files are written.

### Dependencies And Integration Points
It includes `filebench.h`, `ipc.h`, `gamma_dist.h`, and `cvars/mtwist/mtwist.h`. Variables and parser-created random distributions use `randdist_t`; fileset picking and flowops use `fb_random64` for offsets and random selections.

### Risks
`fb_random64` subtracts `round` from `max` without guarding `round > max`, which can underflow. Table initialization logs but does not abort if percentages do not total exactly 100, leaving uninitialized lookup slots possible. `erand48` source state is per distribution, while mtwist default state may be shared. Rounding uses floating-point conversion for large integers, which can lose precision near `UINT64_MAX`.

### Test Signals
Tests should cover max/round boundaries, avd-backed random validation, deterministic seeded generator mode, uniform/gamma/table distribution initialization, malformed probability tables, and 32-bit/64-bit macro selection via `filebench.h`.
