# sources/test-tools/syzkaller/prog/any_test.go

Purpose: validates `ANY` pointer classification and squashing behavior.

Important APIs/types/functions: `TestIsComplexPtr` enumerates all statically squashable pointer element types and compares them with randomly generated complex pointers. `TestSquash` deserializes hand-written programs, invokes `Target.isComplexPtr`, `ArgContainsAny`, and `squashPtr`, then compares serialized output.

Control flow and state: random target-wide generation is skipped in short/race-heavy modes to control runtime. `TestSquash` mutates the same pointer twice to prove squashing is idempotent and that the pointer remains size-stable after conversion.

Dependencies and integration: uses target test helpers from `export_test.go`, generated test descriptions, `Deserialize`, `Serialize`, and the `any.go` implementation. The tests exercise integration with parser support for `ANY=` and serializer output.

Risks: `TestIsComplexPtr` is probabilistic and only requires 90% runtime generation coverage, so rare generator coverage regressions can be noisy. Exact serialized strings make `TestSquash` sensitive to intentional format changes.

Test signals: strong targeted checks for blob/resource packing, endian byte order, padding, unsupported overlays, inout pointers, filename unions, and duplicate squashing.
