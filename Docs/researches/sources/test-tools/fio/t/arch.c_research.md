# sources/test-tools/fio/t/arch.c

## Purpose
`t/arch.c` is a tiny test-support definition file that provides architecture globals needed by fio library code when building standalone tests.

## Important APIs, Types, And Functions
It includes `../arch/arch.h` and defines `unsigned long arch_flags = 0;` and `int arch_random;`.

## Control Flow
There is no runtime control flow. The file satisfies linker requirements for tests that include code expecting these globals.

## State And Persistence Behavior
The globals are process-local test state and start at zero/default initialization. No persistent state exists.

## Dependencies And Integration Points
Standalone test binaries can link this file when they use fio architecture helpers without linking the full fio runtime.

## Risks And Edge Cases
Because it hardcodes neutral values, tests using it may not exercise architecture-specific flags or random-device behavior. If production code starts requiring initialized `arch_random`, this stub may mask missing setup.

## Test Signals
The primary signal is successful linking/running of standalone tests. Architecture-specific tests should avoid this stub or explicitly set the globals.
