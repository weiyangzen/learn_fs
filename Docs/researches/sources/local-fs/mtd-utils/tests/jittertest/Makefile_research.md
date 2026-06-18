# File Research: sources/local-fs/mtd-utils/tests/jittertest/Makefile

## Purpose
Builds the jitter measurement tools.

## Key Elements
Compiles `JitterTest` with `-O3 -Wall -fomit-frame-pointer -lm` and `plotJittervsFill` with the same flags. Contains a historical `makedepend` dependency block.

## Dependencies
Uses `gcc`, math library, and old system include dependency paths from Red Hat/i386-era tooling.

## Behavior/Risks
`clean` removes `JitterTest` but not `plotJittervsFill`, leaving a built binary behind.
