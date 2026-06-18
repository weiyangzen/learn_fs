# sources/security-integrity/selinux/python/sepolgen/tests/test_module.py

## Purpose
This file tests that `sepolgen.module.ModuleCompiler` can produce a compiled SELinux policy package from a `.te` fixture under both explicit and instance-configured refpolicy modes.

## Important Tests And Exercised APIs
`TestModuleCompiler.test()` creates a `ModuleCompiler`, calls `create_module_package("module_compile_test.te", refpolicy=True)`, verifies `module_compile_test.pp` exists with `os.stat()`, deletes it, then sets `mc.refpolicy = True` and calls `create_module_package(..., refpolicy=False)` to verify instance state is honored.

## Control Flow
The test is linear and file-system based. It delegates all real compilation behavior to `ModuleCompiler`, then checks only for the package artifact.

## State And Persistence
It creates and removes `module_compile_test.pp`. The tests Makefile also cleans `.fc`, `.if`, `.pp`, and related temporary outputs because the compiler may generate more than the package in failure or intermediate paths.

## Dependencies And Integration Points
It depends on a local `module_compile_test.te` fixture and on external SELinux policy compilation tools used by `ModuleCompiler`. It imports `os` for artifact checks and removal.

## Risks And Edge Cases
The test can fail in environments without SELinux build tooling even if Python code is correct. It checks artifact existence only, not package content or compiler command diagnostics. Fixed filenames make concurrent test execution unsafe in the same directory.

## Test Signals
This is an integration smoke test for module compilation and refpolicy flag handling. It provides little granularity for diagnosing compilation failures.
