# sources/object-store/apache-ozone/hadoop-hdds/dev-support/checkstyle/suppressions.xml

## Purpose
This file defines Checkstyle suppression rules for known HDDS/Hadoop source areas where the main `checkstyle.xml` rules are intentionally relaxed. It is a build-time lint configuration companion, not runtime code.

## Important modules and entries
- Root element: `suppressions`, using Checkstyle DTD `suppressions_1_1.dtd`.
- Suppresses `JavadocPackage` for any `src/test` path.
- Suppresses `JavadocPackage` for `src/main/java/org/apache/hadoop/io/erasurecode/rawcoder`.
- Suppresses `IllegalImport` and `MissingJavadocType` for `src/test/java/org/apache/hadoop/fs/contract/.*java`.
- Suppresses `IllegalImport` for `src/test/java/org/apache/hadoop/tools/contract/.*java`.
- Suppresses all checks for `src/main/java/org/apache/hadoop/.*_/.*java`, which appears intended for generated or underscore-suffixed compatibility package paths.

## Control flow
When Checkstyle is configured with this suppression file, each violation is matched against the `checks` regex/name and `files` regex. Matching violations are discarded before reporting. The suppression decisions are declarative and order-independent for these entries.

## State and persistence
The file has no mutable state. Its persistent behavior is to hide matching Checkstyle findings across all builds that include this suppressions file.

## Dependencies and integration points
It depends on Checkstyle suppression support and on the build wiring that points Checkstyle at this file. It integrates tightly with `dev-support/checkstyle/checkstyle.xml`, especially the `JavadocPackage`, `IllegalImport`, and `MissingJavadocType` checks.

## Risks and edge cases
- File regexes are path-format sensitive. Some entries use forward slashes only while the first uses `[\\/]`; Windows or alternate path normalization can affect matches.
- `checks=".*"` for underscore package paths suppresses every rule and can mask serious style or correctness issues if the regex catches more code than intended.
- Suppressing test Javadocs reduces noise but also weakens documentation checks for public test utilities.
- If package paths are moved, suppressions may silently stop applying or continue applying to unintended files.

## Test signals
Run the configured Checkstyle task against representative files in the suppressed paths. Violations for `JavadocPackage` under `src/test` should be ignored, `IllegalImport` in the listed contract test paths should be ignored, and the same violations outside those paths should still be reported. A path separator variation test is useful if the build supports multiple operating systems.
