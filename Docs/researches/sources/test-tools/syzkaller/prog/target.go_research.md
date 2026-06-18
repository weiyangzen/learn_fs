## sources/test-tools/syzkaller/prog/target.go

Purpose: defines target OS/arch metadata registration, lazy initialization, link restoration, glob handling, special-generation API, program builder, and KFuzzTest syscall lookup.

Important APIs/types/functions: `Target`, `RegisterTarget`, `GetTarget`, `AllTargets`, `Extend`, `lazyInit`, `initTarget`, `initUselessHints`, `initRelatedFields`, `GetConst`, `sanitize`, `RestoreLinks`, `restoreLinks`, `DefaultChoiceTable`, `NoAutoChoiceTable`, `RequiredGlobs`, `UpdateGlobs`, `requiredGlobs`, `populateGlob`, `Gen`, `Builder`, `MakeProgGen`, `Append`, `Allocate`, `AllocateVMA`, `Finalize`, and `KFuzzTestRunID`.

Control flow: targets are registered by `os/arch`, lazily filled with generated descriptions, linked, indexed, enriched with resource constructors and hints, then target-specific init hooks add mmap, neutralization, special types, and constants. `restoreLinks` assigns global type refs and replaces compiler `Ref` placeholders.

State and persistence: global `targets` map and atomic global `typeRefs` store type references. Per-target maps cache syscalls, constants, flags, resources, and default choice table.

Dependencies/integration: central integration point for generated sys descriptions, OS init packages, random generation, validation, serialization, and tools.

Risks: global type refs require locking and unique assignment. Lazy init order is important: arch init depends on filled maps. Special pointer and filename length bounds are validated to protect generation.

Test signals: `target_test.go`, `prog_test.go`, and package-wide tests cover glob behavior, initialization, choice tables, special types, and target access.
