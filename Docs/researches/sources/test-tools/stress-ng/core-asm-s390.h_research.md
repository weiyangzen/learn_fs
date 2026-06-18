# sources/test-tools/stress-ng/core-asm-s390.h

Purpose: s390 timestamp clock helper.

Important APIs and control flow: `stress_asm_s390_stck` emits `stck` and returns the 64-bit tick value under `STRESS_ARCH_S390`.

State and persistence: stateless hardware read.

Dependencies and integration: used by time/cycle-sensitive stressors on s390.

Risks and test signals: assembler constraint correctness is the key portability risk. Signal is s390 compilation and timestamp-based stressor sanity.
