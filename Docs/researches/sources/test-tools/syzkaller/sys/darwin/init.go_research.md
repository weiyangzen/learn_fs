## sources/test-tools/syzkaller/sys/darwin/init.go

Purpose: target-specific initialization for Darwin syzkaller targets.

Important APIs/types/functions: `InitTarget` and local `arch` wrapper containing `*targets.UnixNeutralizer`.

Control flow: constructs a Unix neutralizer, sets `target.MakeDataMmap` to a POSIX mmap helper with Darwin-specific flags, and assigns neutralization to the generic Unix neutralizer.

State and persistence: mutates in-memory `prog.Target` fields during lazy init. No persistence.

Dependencies/integration: depends on `prog.Target` and `sys/targets` helpers. Called through generated target registration.

Risks: Darwin-specific safety depends mostly on the generic Unix neutralizer. Incorrect mmap helper flags would affect generated memory setup programs.

Test signals: covered indirectly by target initialization and program generation tests over all targets.
