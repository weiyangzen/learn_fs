# sources/test-tools/syzkaller/sys/test/init.go

Purpose: initializes syzkaller's synthetic test OS target.

Important APIs/types/functions: `InitTarget(target *prog.Target)`.

Control flow: assigns `MakeDataMmap` to the syz pseudo-mmap helper and sets `SpecialFileLenghts` to `[3, 256]` for test generation behavior.

State and persistence: no persistent state.

Dependencies and integration points: used by generated sys registration and many tests that target `targets.TestOS`.

Risks: typo-preserved field `SpecialFileLenghts` must match existing `prog.Target` API. Changing lengths can alter test corpus behavior.

Test signals: indirect repository-wide test OS usage.
