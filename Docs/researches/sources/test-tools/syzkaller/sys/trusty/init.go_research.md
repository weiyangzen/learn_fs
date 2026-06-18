# sources/test-tools/syzkaller/sys/trusty/init.go

Purpose: initializes Trusty target data mapping.

Important APIs/types/functions: `InitTarget(target *prog.Target)`.

Control flow: assigns `target.MakeDataMmap = targets.MakeSyzMmap(target)`.

State and persistence: no persistent state.

Dependencies and integration points: connects Trusty generated target metadata to the shared syz pseudo-mmap setup.

Risks: assumes Trusty executor supports `syz_mmap`.

Test signals: no direct tests in this subset.
