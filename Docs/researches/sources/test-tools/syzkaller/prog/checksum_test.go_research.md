# sources/test-tools/syzkaller/prog/checksum_test.go

Purpose: stress-tests checksum descriptor generation on generated and mutated Linux/amd64 programs.

Important APIs/types/functions: `TestChecksumCalcRandom` uses `InitTest`, `DefaultChoiceTable`, `Target.Generate`, `Prog.Mutate`, and exported `CalcChecksumsCall`.

Control flow and state: for each randomized iteration it generates a 10-call program, calculates checksum info for every call, mutates the program, and recalculates checksum info. It does not assert exact descriptors; it relies on panics/failures to catch invalid traversal or descriptor assumptions.

Dependencies and integration: package is `prog_test`, importing `prog` through dot import and `_ "github.com/google/syzkaller/sys"` to register syscall descriptions. Exported test aliases are provided by `export_test.go`.

Risks: random stress can miss specific pseudo-header edge cases, while failures may depend on target descriptions changing. It is a panic-safety test rather than a golden-output test.

Test signals: broad randomized coverage for checksum field discovery across generation and mutation; exact checksum wire-format coverage lives in `encodingexec_test.go`.
