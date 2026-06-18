# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/GlobPattern.java

## Purpose
POSIX-style glob pattern compiler with brace expansion, using shaded-compatible `com.google.re2j.Pattern`.

## Important APIs and types
Constructor and `set` compile a glob string. `compile` is a static shortcut. `matches` tests a candidate string. `compiled` exposes the RE2/J pattern. `hasWildcard` reports whether glob wildcard constructs were seen.

## Control flow and state
`set` translates glob syntax into regex: `*` and `?` become dot-based wildcards, braces become non-capturing groups with commas as alternation, character classes are tracked, selected regex metacharacters are escaped, and `[!` becomes `[^`. It rejects missing escaped characters, unclosed character classes, and unclosed groups. The compiled regex uses `Pattern.DOTALL`.

## Dependencies and integration points
Copied from Hadoop to avoid shaded/non-shaded RE2/J signature mismatch. Used by utilities needing glob matching without Java regex backtracking risk.

## Risks and test signals
Tests should cover literal escaping, star/question semantics, brace alternatives, nested or unclosed braces, character classes, negated classes, trailing backslash, wildcard detection, and invalid pattern exceptions. The `*` translation appends `.` before the original `*`, producing regex `.*`; this is intentional through fall-through.
