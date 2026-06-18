## sources/test-tools/syzkaller/pkg/kfuzztest/kfuzztest.go

Purpose: public KFuzzTest API for extracting generated descriptions/data and activating discovered targets in a syzkaller `prog.Target`.

Important APIs/types/functions: `SyzField`, `SyzStruct`, `SyzFunc`, `ConstraintType`, `SyzConstraint`, `AnnotationAttribute`, `SyzAnnotation`, `ExtractDescription`, `KFuzzTestData`, `ExtractData`, `ActivateKFuzzTargets`, `GetTestName`, `GetInputFilepath`, and constants for syscall/debugfs naming.

Control flow: `ExtractDescription` runs extractor then builder. `extractData` parses generated syzlang, compiles it for Linux/AMD64, filters syscalls with `KFuzzTest` attr, restores links, and packages calls/resources/types. `ExtractData` caches one extraction with `sync.Once`. `ActivateKFuzzTargets` extends a target with those calls. `GetTestName` validates `syz_kfuzztest_run$` naming.

State and persistence: global `extractState` caches one vmlinux’s data per process. No disk persistence.

Dependencies and integration: integrates extractor/builder, syzkaller AST/compiler/prog target extension, and Linux/AMD64 target metadata.

Risks: cache ignores `vmlinuxPath`, so multiple different images in one process are unsupported. Architecture is hard-coded to Linux/AMD64. `ConstraintType.String` indexes a fixed array and can panic for invalid values.

Test signals: description generation covers extraction/description; manager/executor consume activated calls.
