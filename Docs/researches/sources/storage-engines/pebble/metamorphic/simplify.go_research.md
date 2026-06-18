<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/metamorphic/simplify.go -->
## sources/storage-engines/pebble/metamorphic/simplify.go

Purpose: rewrites metamorphic operation streams to use a smaller ordered key set, making failing histories easier to inspect and reduce. The simplification is intentionally not guaranteed to preserve semantics.

Important APIs and functions: `TryToSimplifyKeys(keyFormat, opsData, retainSuffixes)` parses formatted operation data, discovers distinct keys or distinct prefixes, maps them to lowercase letters `a` through `z`, rewrites operation keys in-place through each op's `rewriteKeys`, and returns reformatted operations. `sortedKeys` sorts discovered keys with the key format comparer.

Control flow: the function parses with the supplied formatted key and suffix parsers. It makes a first rewrite pass only to collect keys while returning the original key. If there are more than 26 distinct rewrite targets it returns nil. It sorts keys by the configured comparer, assigns ordinal letters, then makes a second rewrite pass. With `retainSuffixes`, only prefixes are ordinalized and suffix bytes are appended unchanged.

State and persistence: all state is transient maps/slices and parsed operations. It does not write files; callers decide how to use returned operation data.

Dependencies and integration: depends on parser correctness, operation `rewriteKeys` implementations, `formatOps`, and `KeyFormat.Comparer.Split/Compare`. Integrates with testkey/cockroach key formats through formatted parser hooks.

Risks and edge cases: the semantic warning is important: collapsing key bytes can change prefix relationships, separator behavior, and range interactions. Returning nil on more than 26 keys can surprise callers that do not distinguish nil from an empty operation stream.

Test signals: `simplify_test.go` uses datadriven cases in `testdata/simplify`, including the suffix-retention mode.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/metamorphic/simplify.go -->
