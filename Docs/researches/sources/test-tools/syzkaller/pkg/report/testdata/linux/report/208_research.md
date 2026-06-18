<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/208 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/208

## Purpose
This fixture validates corrupted suspicious-RCU warning parsing under fault injection and crypto/RDS noise. Expected title is `WARNING: suspicious RCU usage`, type `WARNING`, and `CORRUPTED: Y`.

## Important APIs, Types, And Functions
The 296-line log contains `WARNING: suspicious RCU usage`, `FAULT_INJECTION: forcing a failure`, held `rcu_read_lock` context in `__rds_conn_create`, crypto allocation failures, and a later sleeping-function invalid-context BUG. Important frames include `__rds_conn_create`, `lockdep_rcu_suspicious`, `___might_sleep`, `__might_sleep`, `should_fail`, `should_failslab`, `crypto_create_tfm`, `crypto_alloc_skcipher`, `cryptd_alloc_skcipher`, `simd_skcipher_init`, `drbg_init_sym_kernel`, `drbg_kcapi_seed`, `crypto_rng_reset`, `alg_setsockopt`, and `rds_loop_conn_alloc`.

## Control Flow
The Linux reporter should anchor on the suspicious RCU warning but treat the report as corrupted because fault-injection, crypto, CLUSTERIP, and RDS diagnostics are interleaved. The expected title is generic, not allocator-specific. Runtime flow includes AF_ALG setsockopt/DRBG setup and RDS connection creation while RCU context warnings are emitted.

## State And Persistence
Persistent state is the expected metadata and raw mixed log. Volatile state includes fault-injection state, crypto algorithm allocation failures, RCU lock context, PIDs, addresses, and socket options.

## Dependencies And Integration Points
It depends on suspicious-RCU matchers, corrupted-output heuristics, fault-injection noise filtering, and warning type mapping. It integrates with report tests as a high-noise RCU warning case distinct from the cleaner RDS fixtures.

## Risks
Parser regressions may choose crypto functions, RDS allocator functions, or the later sleeping-function warning as the title. It may also return `LOCKDEP` instead of the expected `WARNING`.

## Test Signals
Assert title `WARNING: suspicious RCU usage`, type `WARNING`, and corruption true. The report should preserve the illegal RCU critical-section evidence while tolerating fault-injection and crypto noise.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/208 -->
