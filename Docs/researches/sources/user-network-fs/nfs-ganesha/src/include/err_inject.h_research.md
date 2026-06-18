# sources/user-network-fs/nfs-ganesha/src/include/err_inject.h

## Purpose
`err_inject.h` is a compile-time gated interface for worker-delay error injection. It is only active when `_ERROR_INJECTION` is defined.

## Important APIs, Types, And Functions
When enabled, the header declares global delay controls `worker_delay_time` and `next_worker_delay_time`, plus `init_error_injector`. With `_ERROR_INJECTION` disabled, it contributes no declarations.

## Control Flow
The intended flow is build-time opt-in, initialize the injector, then have worker code consult or update the delay globals to introduce controlled timing faults. The header itself contains no logic.

## State And Persistence
The active state is global process memory. There is no persistence; injected behavior lasts only for the process and build configuration.

## Dependencies And Integration Points
It has no includes. Integration depends on code compiled under `_ERROR_INJECTION` that defines and uses these globals. It is a testing/debug hook rather than production API.

## Risks
Because declarations vanish outside error-injection builds, all usage must be preprocessor-gated. Global mutable delay state is inherently racy unless implementation adds synchronization. Leaving `_ERROR_INJECTION` enabled in production would intentionally alter worker timing.

## Test Signals
Build tests should include injection enabled and disabled. Runtime tests should verify injector initialization, one-shot versus persistent delay behavior, and absence of unresolved symbols in normal builds.
