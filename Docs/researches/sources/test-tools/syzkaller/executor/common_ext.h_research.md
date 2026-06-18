# sources/test-tools/syzkaller/executor/common_ext.h

Purpose: This extension-point header is intentionally mostly empty. It lets downstream or non-mainline syzkaller users add pseudo-syscalls and setup hooks without changing the main executor templates.

Important APIs and types: The file documents expected extension conventions: pseudo-syscalls should start with `syz_ext_`; defining `SYZ_HAVE_SETUP_EXT` with `void setup_ext()` adds VM-level setup; defining `SYZ_HAVE_SETUP_EXT_TEST` with `void setup_ext_test()` adds per-test-process setup.

Control flow and state: There is no executable code or persistent state in the default file. `common.h` includes it unless `SYZ_TEST_COMMON_EXT_EXAMPLE` selects the example implementation. If macros are defined by a modified copy, `common.h` calls `setup_ext()` during csource `main` setup and `setup_ext_test()` in forked test children.

Dependencies and integration points: The header is included by both executor and C reproducers. It depends on the surrounding generated executor symbols only when an extension implementation uses them.

Risks and test signals: The main risk is that extensions run in privileged setup paths and can silently alter executor behavior across all generated programs. Tests should verify default builds remain no-op, extension pseudo-syscalls are stripped/included according to `SYZ_*` defines, and setup hooks are called at the documented lifecycle points.
