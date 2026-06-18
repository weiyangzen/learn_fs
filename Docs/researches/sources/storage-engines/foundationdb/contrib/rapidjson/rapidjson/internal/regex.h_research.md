# sources/storage-engines/foundationdb/contrib/rapidjson/rapidjson/internal/regex.h

Purpose: This header implements RapidJSON's internal ECMAScript-subset regular expression engine, primarily for JSON Schema `pattern` validation.

Important APIs and types: `GenericRegex<Encoding, Allocator>` parses a pattern into a Thompson NFA and exposes `IsValid()`, `Match(InputStream&)`, `Match(const Ch*)`, `Search(InputStream&)`, and `Search(const Ch*)`. `Regex` aliases UTF-8 default allocation. Internal state includes `State`, `Range`, `Frag`, parser operator stacks, range lists, and mutable search state sets.

Control flow: Construction decodes the source pattern into codepoints, parses operators, groups, character classes, anchors, and quantifiers, then patches fragments into an NFA ending at a match state. Quantifiers clone fragments as needed for bounded repetitions. Search maintains current and next state lists, expands split states through `AddState()`, tests codepoints and ranges, and honors `^`/`$` anchoring.

State and persistence behavior: The compiled regex persists in memory as stack-backed `states_` and `ranges_`; `stateSet_`, `state0_`, and `state1_` are mutable search buffers. No filesystem persistence exists. Match/search methods are logically const but mutate internal buffers, so shared concurrent use is risky.

Dependencies and integration points: It depends on `allocators.h`, `stream.h`, and `internal::Stack`. Schema validation uses it for string pattern checks. Encoding decoding defines what a pattern character means.

Risks: Unsupported escapes fail parsing. Bounded repetition can clone many states and consume memory. `stateSet_` is allocated from the states allocator and manually freed. Mutable search buffers make thread safety non-obvious. Anchoring behavior differs between `Match()` and `Search()`.

Test signals: Cover literals, alternation, concatenation, groups, `?`, `*`, `+`, `{n}`, `{n,}`, `{n,m}`, anchors, dot, class ranges, negated classes, escaped metacharacters, invalid patterns, Unicode patterns, schema integration, and concurrent-use expectations.
