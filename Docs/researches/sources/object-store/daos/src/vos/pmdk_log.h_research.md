# sources/object-store/daos/src/vos/pmdk_log.h

## Purpose
Public declaration for attaching DAOS logging to PMDK logging.

## Important APIs, Types, And Functions
Declares `int pmdk_log_attach(void);` behind include guard `__PMDK_LOG__`.

## Control Flow
Callers include the header and invoke `pmdk_log_attach` during PMDK/VOS initialization to register the PMDK log callback if the build supports it.

## State And Persistence
No state is defined here.

## Dependencies And Integration
Implemented by `pmdk_log.c`; integration depends on DAOS initialization order and PMDK build configuration.

## Risks
The header exposes no build-configuration indication, so callers must rely on implementation behavior in non-PMEM builds.

## Test Signals
Compile coverage is the primary signal; runtime attach behavior is tested through `pmdk_log.c`.
