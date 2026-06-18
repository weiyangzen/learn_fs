# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/42

Purpose: Linux reporter parse fixture for syzkaller. It expects `UBSAN: undefined-behaviour in corrupted`, type `UBSAN`, corrupted `Y`, panicked `N`. This is an intentionally tiny corrupted UBSAN fixture.

Important APIs, types, and functions: the file exercises the Linux reporter's ability to return a crash with a corrupted title when stack/function data is insufficient. It still uses the normal `ContainsCrash`, `Parse`, and `ParseFrom` test path, but no meaningful stack functions are present.

Control flow: after headers, only two log lines remain. The parser must detect UBSAN undefined-behaviour syntax but mark the extracted function as corrupted instead of inventing a frame.

State and persistence behavior: the fixture persists the corruption expectation in `CORRUPTED: Y`; runtime parser state is temporary.

Dependencies, integration points, risks, and test signals: this protects negative/partial-report handling. Risks include treating missing stack context as a parser failure or misclassifying corruption as a clean report. Passing tests require UBSAN type, title ending in `corrupted`, corrupted `Y`, and no panic.
