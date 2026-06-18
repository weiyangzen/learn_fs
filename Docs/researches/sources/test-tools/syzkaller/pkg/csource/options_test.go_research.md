# sources/test-tools/syzkaller/pkg/csource/options_test.go

This test file validates option serialization compatibility, option-space enumeration, and feature flag parsing for csource.

`TestParseOptions` round-trips representative single-field option variations through JSON. `TestParseOptionsCanned` verifies current and legacy dashboard payloads, including older fields like `collide`, `fault`, `EnableTun`, empty sandbox encoding, Android sandbox args, and namespace sandbox args. `allOptionsSingle`, `allOptionsPermutations`, `dedup`, and `enumerateField` generate valid option sets while filtering through `Options.Check`.

`TestParseFeaturesFlags` checks `-enable` and `-disable` combinations such as `none`, `all`, empty strings, selected feature subsets, and default-enabled/default-disabled behavior. State is test-local; dependencies are `reflect`, `math` boundary values for sandbox args, target OS constants, and the option parser under test.

Integration signal is high for backward compatibility because dashboard reproducers may contain old serialized formats. Risks include missing newly added `Options` fields in enumeration expectations, legacy parser breakage, feature map drift, and duplicate or invalid combinations slipping into generation tests.
