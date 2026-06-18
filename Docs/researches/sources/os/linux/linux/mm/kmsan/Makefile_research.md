# File Research: sources/os/linux/linux/mm/kmsan/Makefile

## Role

Build rules for KernelMemorySanitizer runtime objects and KMSAN KUnit tests.

## Contents

- Builds KMSAN runtime objects into `obj-y`:
  - `core.o`
  - `instrumentation.o`
  - `init.o`
  - `hooks.o`
  - `report.o`
  - `shadow.o`
- Disables sanitizers and coverage for the runtime:
  - `KMSAN_SANITIZE := n`
  - `KCOV_INSTRUMENT := n`
  - `UBSAN_SANITIZE := n`
- Adds runtime C flags:
  - `-fno-stack-protector`
  - optional `-fno-conserve-stack`
  - `-DDISABLE_BRANCH_PROFILING`
- Removes ftrace flags from every runtime object to avoid recursion.
- Applies the runtime flags uniformly to all KMSAN runtime objects.
- Builds `kmsan_test.o` only under `CONFIG_KMSAN_KUNIT_TEST`.
- Enables KMSAN instrumentation for `kmsan_test.o` and disables the compiler `uninitialized` warning there.

## Research Notes

The Makefile is safety-critical because the sanitizer runtime must not recursively instrument itself with KMSAN, ftrace, KCOV, UBSAN, stack protector, or branch profiling. The test object is intentionally different: it is instrumented so it can validate KMSAN behavior.
