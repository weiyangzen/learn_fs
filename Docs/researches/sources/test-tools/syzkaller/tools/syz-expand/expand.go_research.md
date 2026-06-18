# sources/test-tools/syzkaller/tools/syz-expand/expand.go

Purpose: `syz-expand` parses one syzkaller program and prints it in verbose form with defaults expanded.

Important APIs and flow: `main` parses `-os`, `-arch`, `-prog`, and `-strict`, resolves the target, reads the program file, selects `prog.Strict` or `prog.NonStrict`, deserializes the program, and prints `SerializeVerbose()`.

State and persistence: read-only except stdout/stderr. No persistent state is created.

Dependencies and integration: depends on `prog.GetTarget`, all `sys` descriptions, and program serialization/deserialization APIs. It is a developer inspection tool for syzkaller DSL programs.

Risks: exits directly on missing file, target, or parse errors. Strict mode may reject programs accepted by manager workflows.

Test signals: no direct test. Existing parser/serializer tests cover the underlying behavior.
