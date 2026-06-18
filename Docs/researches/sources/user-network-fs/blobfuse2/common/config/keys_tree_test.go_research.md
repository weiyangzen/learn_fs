# sources/user-network-fs/blobfuse2/common/config/keys_tree_test.go
## sources/user-network-fs/blobfuse2/common/config/keys_tree_test.go

Purpose: unit tests for the low-level parsing and primitive-kind helpers in `keys_tree.go`.

Important APIs/helpers: `keysTreeTestSuite`, `parseVal`, `TestParseValue`, `TestParseValueErr`, `TestIsPrimitiveType`, and `TestIsNotPrimitiveType`.

Control flow: `TestParseValue` iterates through strings representing booleans, signed/unsigned integers, floats, complex numbers, and strings, calling `parseValue` for each `reflect.Kind` and asserting the typed result. `TestParseValueErr` feeds non-parsable strings to all non-string primitive kinds and expects nil. The primitive tests assert the exact kinds considered primitive by `isPrimitiveType`.

State and persistence: no external state; pure in-memory tests.

Dependencies/integration: reflect, testify suite/assert, and the unexported helpers because the tests live in the same `config` package.

Risks: tests do not cover `Tree.Insert`, `GetSubTree`, `Merge`, `MergeWithKey`, struct tags, pointer fields, nil pointer behavior, or `assignToField` directly. Complex expected values are untyped constants and rely on `EqualValues`.

Test signals: confirms the accepted primitive surface and that parse failures return nil rather than errors, which is important because config overlay silently ignores invalid env/flag strings.
