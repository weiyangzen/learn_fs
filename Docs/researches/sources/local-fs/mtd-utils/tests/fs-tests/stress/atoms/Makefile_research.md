# File Research: sources/local-fs/mtd-utils/tests/fs-tests/stress/atoms/Makefile

## Purpose
Builds atomic stress-test executables.

## Key Elements
Targets `stress_1`, `stress_2`, `stress_3`, `pdfrun`, `rndwrite00`, `fwrite00`, `rmdir00`, `rndrm00`, `rndrm99`, and `gcd_hupper`, linking each with `../../lib/tests.o`. The `tests` target runs representative invocations.

## Dependencies
Uses `gcc`, include path `../../lib`, and shared test library object.

## Behavior/Risks
Contains a likely stale dependency rule `../lib/tests.o: ../../lib/tests.h` while targets use `../../lib/tests.o`; normal linking still depends on the actual object.
