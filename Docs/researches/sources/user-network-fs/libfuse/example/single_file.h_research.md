# sources/user-network-fs/libfuse/example/single_file.h

## Purpose
`single_file.h` declares the shared state, option keys, numeric helpers, and high-level/low-level operation helpers implemented by `single_file.c`. It lets service examples include only the API style they use through `USE_SINGLE_FILE_LL_API` and `USE_SINGLE_FILE_HL_API`.

## Important APIs, Types, and Functions
Inline helpers include `round_up`, `round_down`, `howmany`, `b_to_fsbt`, `b_to_fsb`, and `fsb_to_b`. `struct single_file` defines the backing fd, logical geometry, mode, flags, timestamps, and mutex. `enum single_file_opt_keys` and `SINGLE_FILE_OPT_KEYS` define FUSE option parser keys for `ro`, `rw`, `require_bdev`, `dio`, `nodio`, `sync`, `nosync`, `size=`, and `blocksize=`. The header declares service open/configure/close, pread/pwrite, bounds checks, and conditional low-level/high-level handlers.

## Control Flow
Including files define `USE_SINGLE_FILE_LL_API` or `USE_SINGLE_FILE_HL_API` before including this header, which exposes the matching callback prototypes. Runtime control flow is in `single_file.c`; this header shapes how service files build operation tables and parse options.

## State and Persistence
The header declares `extern struct single_file single_file`, a single global process state object. It does not persist anything by itself. Inline block conversion helpers read `single_file.blocksize`, so they depend on `single_file_configure()` having initialized block size before use.

## Dependencies and Integration Points
The declarations assume libfuse types such as `fuse_req_t`, `fuse_ino_t`, `struct fuse_file_info`, `fuse_fill_dir_t`, and `struct fuse_args` are visible from prior includes. It forward-declares `struct fuse_service` for service-mediated backing-file open. It is included by `single_file.c`, `service_hl.c`, and `service_ll.c`.

## Risks
Because inline helpers divide by `single_file.blocksize`, misuse before configuration can divide by zero. The conditional prototype blocks can hide needed declarations if callers forget the macro; the header emits only a preprocessor warning when neither API macro is defined. Global state makes multiple independent single-file instances in one process unsupported.

## Test Signals
Build both service examples to verify macro-gated prototypes match implementations. Exercise option parsing using `SINGLE_FILE_OPT_KEYS` and validate block conversion helpers after setting blocksize. Compile a file without API macros and confirm the warning appears.
