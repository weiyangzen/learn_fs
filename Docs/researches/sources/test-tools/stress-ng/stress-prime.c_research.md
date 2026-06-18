# sources/test-tools/stress-ng/stress-prime.c

Purpose: `stress-prime.c` implements the `prime` stressor, using GMP to find successive primes from configurable starting values and growth methods.

Important APIs/types/functions: the implementation requires GMP, libgmp, and siglongjmp; MPFR is optional for parsing floating-point start values. `stress_prime_start()` parses `--prime-start` as an `mpz_t` integer or MPFR floating value converted to integer and rejects negatives. `stress_prime_alarm_handler()` stops the stressor on SIGALRM and longjmps after repeated alarms. `stress_prime()` owns GMP values and the prime loop.

Control flow: the stressor initializes `mpz_t` values for start, current prime, and factorial multiplier, reads `prime-method`, `prime-progress`, and `prime-start`, parses the start or defaults to 1, disables progress for nonzero instances, synchronizes, installs the SIGALRM handler, and loops. Each iteration times `mpz_nextprime(value, start)`, advances `start` by factorial multiplication, value+2, power-of-two growth, or power-of-ten growth, increments bogo ops, records digit count, and optionally prints progress every 60 seconds.

State and persistence behavior: state is GMP heap-backed integers, progress timing, bogo counter, and signal longjmp state. On normal exit it clears GMP objects; after signal longjmp it intentionally skips cleanup to avoid heap corruption risks. No files are created.

Dependencies and integration points: GMP, optional MPFR, stress-ng settings/method parsing, signal handling, metrics, sync barriers, and `CLASS_CPU | CLASS_INTEGER | CLASS_COMPUTE` registration with `VERIFY_NONE`.

Risks: very large starts or multiplicative methods can create enormous GMP values and long `mpz_nextprime` calls. Signal interruption during GMP work is handled conservatively but can leak GMP allocations on longjmp. Floating start parsing depends on MPFR availability.

Test signals: `--prime` should emit primes/sec, primes found, and largest-digit metrics. Useful variants include all `--prime-method` values, integer and scientific-notation `--prime-start`, invalid negative starts, progress output on instance zero, and unsupported builds without GMP.
