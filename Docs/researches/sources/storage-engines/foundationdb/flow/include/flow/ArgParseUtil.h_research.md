# sources/storage-engines/foundationdb/flow/include/flow/ArgParseUtil.h

Purpose: helper for extracting normalized command-line argument keys with a specific prefix.

Important APIs/types/functions: `extractPrefixedArgument(std::string prefix, std::string arg)`.

Control flow: verifies `arg` starts with `prefix`, has an extra separator character, and that separator is `-` or `_`. It then strips the prefix plus separator and converts all hyphens in the remaining key to underscores.

State/persistence: no state.

Dependencies/integration: includes `flow/Arena.h` for `Optional<std::string>`. Intended for command-line parsing such as prefixed knobs.

Risks: function is defined in a header without `inline`, which can risk ODR/link issues if included in multiple translation units unless usage/build avoids it. Prefix matching is literal and case-sensitive.

Test signals: unit tests or callers should verify `--prefix-key`, `--prefix_key`, too-short strings, and nonmatching prefixes.
