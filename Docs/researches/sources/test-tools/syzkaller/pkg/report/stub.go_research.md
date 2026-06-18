# Research: sources/test-tools/syzkaller/pkg/report/stub.go

Purpose: placeholder reporter for targets that are known to the constructor table but do not have an implemented parser, currently Windows.

Important APIs/types/functions: `type stub` embeds `config`; `ctorStub` returns a stub instance with no suppressions; `ContainsCrash`, `Parse`, and `Symbolize` all panic with `not implemented`.

Control flow: `NewReporter` can construct the stub through `ctors`, but callers that use it will panic on reporter operations. Test/fuzz setup explicitly skips Windows and filters stub implementations when building fuzz reporters.

State and persistence: no state beyond embedded config and no persistence.

Dependencies and integration points: integrated through `ctors[targets.Windows]`. Its existence lets target selection fail later for unsupported behavior while preserving a constructor entry.

Risks: accidental use in production paths will panic. Any new target mapped to `ctorStub` must be filtered out of fuzz/test loops or implemented before use.

Test signals: fuzz reporter construction skips stubs; generic test iteration skips Windows. A direct test could assert that Windows remains intentionally unsupported until implemented.
