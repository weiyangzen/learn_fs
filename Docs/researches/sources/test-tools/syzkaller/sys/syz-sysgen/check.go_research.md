# sources/test-tools/syzkaller/sys/syz-sysgen/check.go

Purpose: validates that syzlang constants are defined on at least one architecture.

Important APIs/types/functions: `constsAreAllDefined(consts *compiler.ConstFile, constInfo map[string]*compiler.ConstInfo, eh ast.ErrorHandler)`.

Control flow: iterates all extracted const metadata, checks each name with `ConstFile.ExistsAny`, and reports an error through the supplied AST error handler when no architecture defines it.

State and persistence: no persistent state; only appends errors via callback.

Dependencies and integration points: called by `sysgen.go` during per-OS/per-arch generation, except Fuchsia is skipped because it has many known broken constants.

Risks: the check runs after compile, so it can fail generation for stale syzlang references even if the affected arch is not currently targeted.

Test signals: no direct unit test; generation failure is the signal.
