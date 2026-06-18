# sources/storage-engines/foundationdb/fdbserver/swift/tests/Rainbow.swift

Purpose: Provides a tiny ANSI color helper for Swift test output. `RainbowColor` maps named colors to terminal escape sequences and `String` extensions expose `.red`, `.green`, `.yellow`, etc. for readable pass/fail/skip logging.

Important APIs/types/functions: `RainbowColor: String` defines the color escape codes plus `name()`. `String.colored(as:)` wraps the receiver in the selected color and resets to `.default`; computed properties call it for each color.

Control flow: There is no asynchronous or branching runtime flow beyond the enum switch in `name()`. Test code calls the computed properties while printing status lines.

State and persistence behavior: Stateless. It only constructs temporary strings; it does not mutate global state or persist output.

Dependencies and integration points: Pure Swift standard library. Used by `SimpleSwiftTestSuite.swift` and `swift_tests.swift` logging to distinguish skipped, passing, and failing tests. It assumes ANSI-capable stdout/stderr.

Risks: Escape sequences may pollute logs or non-terminal consumers. Color helpers always reset to default, which avoids most bleed-through risk. The file header name appears copied from `swift_test_streams.swift`, a documentation-only mismatch.

Test signals: Indirectly exercised whenever Swift tests print colored status. No explicit assertions are needed beyond ensuring colored output remains valid strings.
