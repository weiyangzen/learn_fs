## sources/test-tools/syzkaller/sys/fuchsia/init.go

Purpose: target-specific initialization for Fuchsia targets.

Important APIs/types/functions: `InitTarget` and go:generate directives for amd64 and arm64 FIDL generation.

Control flow: sets `target.MakeDataMmap` to `targets.MakeSyzMmap`, using syzkaller's synthetic mmap helper rather than POSIX mmap.

State and persistence: mutates only the in-memory target hook. The go:generate comments drive source generation outside runtime.

Dependencies/integration: depends on `prog.Target`, `sys/targets`, and Fuchsia fidlgen output.

Risks: minimal runtime logic; correctness depends on generated descriptions and syz mmap support.

Test signals: indirect target initialization coverage.
