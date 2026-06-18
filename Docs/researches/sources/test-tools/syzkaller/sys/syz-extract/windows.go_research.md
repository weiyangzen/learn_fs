# sources/test-tools/syzkaller/sys/syz-extract/windows.go

Purpose: Windows backend stub for constant extraction.

Important APIs/types/functions: `windows.prepare`, `windows.prepareArch`, and `windows.processFile`.

Control flow: prepare hooks are no-ops. `processFile` calls shared `extract` with Microsoft `cl` and no additional arguments.

State and persistence: only temporary compile artifacts from shared extraction.

Dependencies and integration points: depends on `cl` being present and compatible with the generated source template.

Risks: this is intentionally thin and lacks include/toolchain setup, so environment configuration bears most of the burden.

Test signals: no direct tests.
