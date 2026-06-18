# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/debug.h

This header defines illumos assertion, verification, and compile-time assertion macros. It includes ISA definitions outside standalone builds, base types, and note annotations.

`VERIFY()` always evaluates and calls `assfail()` on false. `ASSERT()` does so only in debug builds and is a no-op otherwise. `ASSERT32` and `ASSERT64` select assertions based on data model.

`IMPLY()` and `EQUIV()` are debug-only logical assertion helpers. The `VERIFY3*` and `ASSERT3*` families compare two values and report the left value, operator, and right value through `assfail3()`. Variants cover boolean, signed, unsigned, pointer, and zero comparisons. `CTASSERT()` maps to C11 `_Static_assert`.

Kernel/fake-kernel declarations include `abort_sequence_enter()` and `debug_enter()`. The `STATIC` macro becomes empty for non-Sun DEBUG builds, otherwise `static`, supporting debug visibility during non-Sun builds.

Research notes:
- `VERIFY*` macros keep side effects in both debug and non-debug builds; `ASSERT*` macros do not.
- `ASSERT3*` macros evaluate arguments once into typed temporaries.
- This is a foundational header frequently used across kernel code.
