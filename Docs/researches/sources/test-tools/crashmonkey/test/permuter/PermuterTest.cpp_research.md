# sources/test-tools/crashmonkey/test/permuter/PermuterTest.cpp

Purpose: comprehensive gtest coverage for the base permuter's epoch construction, barrier handling, checkpoint numbering, overlap detection, sector coalescing, and `epoch_op` sector splitting. It uses a small `TestPermuter` subclass to expose protected internals.

Important APIs/types/functions: `Permuter`, `epoch`, `epoch_op`, `EpochOpSector`, `PermuteTestResult`, `disk_write`, `InitDataVector`, `CoalesceSectors`, `GetEpochs`, `VerifyEpoch`, and HWM flags. Tests cover flush and FUA barriers, unterminated epochs, overlapping writes, split flushes, checkpoint edge cases, metadata counts, sector coalescing, and `ToSectors`.

Control flow: each test builds vectors of synthetic `disk_write` entries with checkpoint/write/barrier flags, initializes a `TestPermuter`, inspects internal epoch vectors, and asserts metadata, barrier, overlap, abs-index, and sector fields. The coalescing tests build `EpochOpSector` vectors directly.

State/persistence behavior: no disk persistence; the state under test is in-memory interpretation of block log entries into crash permutation epochs. Dependencies/integration: validates assumptions used by random and exhaustive crash-state generation.

Risks/test signals: tests rely on synthetic metadata rather than real disk-wrapper logs; `TestPermuter` stubs permutation generation, so only common base behavior is covered. Failures identify regressions in epoch boundary and sector math.
