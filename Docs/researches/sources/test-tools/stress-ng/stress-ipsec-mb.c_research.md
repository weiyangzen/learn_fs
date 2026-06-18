# sources/test-tools/stress-ng/stress-ipsec-mb.c

Purpose: implements `ipsec-mb`, a compute stressor for Intel IPSec MB library job submission across CPU feature backends and crypto/integrity methods.

Important APIs/types/functions: compatibility macros normalize old and new IPSec MB names. `stress_ipsec_features_t` stores required feature bits, init function, support status, and metrics. Method functions cover SHA-512, AES-CBC named `des`, AES-CMAC, AES-CTR, HMAC-MD5, HMAC-SHA1, and HMAC-SHA512. Core helpers include `stress_job_get_next()`, `stress_job_check_status()`, `stress_jobs_done()`, and `stress_ipsec_call_func()`.

Control flow: support checks require x86-64, library headers, library linkage, and feature macros. `stress_ipsec_mb()` validates library version, allocates an `IMB_MGR`, detects CPU features, optionally narrows to one `--ipsec-mb-feature`, fills an aligned 8192-byte data block, then sync-starts. Each loop initializes each supported backend and invokes the selected method or `all`. Method functions allocate aligned outputs, populate job fields, submit jobs, flush completions, count successful jobs as bogo ops, and free buffers. Metrics are emitted per backend.

State and persistence behavior: all data is in process memory: manager state, random keys/IVs, output buffers, and per-feature stats. There is no filesystem persistence.

Dependencies and integration points: tied to Intel IPSec MB API, CPU feature detection, stress-ng settings and metrics, and target architecture gates. Registered as `CLASS_CPU | CLASS_INTEGER | CLASS_COMPUTE`.

Risks: library ABI/version differences are handled partly by macros but remain a compatibility risk. Some method names are historical or imprecise. The HMAC-SHA1 setup uses MD5 one-block helpers for ipad/opad hashes, which should be treated as intentional library stress rather than a correctness reference. Large `--ipsec-mb-jobs` values can allocate substantial memory.

Test signals: cover unsupported-library skip, feature filtering, `--ipsec-mb-method all`, large and minimal job counts, and metrics for each supported backend. Failure signals are incomplete job counts, non-completed job status, allocation failures, or crashes under specific CPU feature initializers.
