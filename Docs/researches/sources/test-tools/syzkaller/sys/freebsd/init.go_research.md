## sources/test-tools/syzkaller/sys/freebsd/init.go

Purpose: target-specific initialization for FreeBSD syzkaller targets.

Important APIs/types/functions: `InitTarget` and local `arch`.

Control flow: creates a Unix neutralizer, sets a POSIX mmap helper with FreeBSD settings, and assigns neutralization to the generic Unix neutralizer.

State and persistence: mutates in-memory target hooks during lazy init. No persistence.

Dependencies/integration: depends on `prog.Target` and `targets.MakeUnixNeutralizer`/`MakePosixMmap`.

Risks: target safety is delegated to generic Unix neutralization. Mmap helper flags must match executor expectations for FreeBSD.

Test signals: indirectly covered by all-target generation and serialization tests.
