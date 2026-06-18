# sources/object-store/apache-ozone/hadoop-hdds/dev-support/checkstyle/checkstyle.xml

## Purpose
This XML file is the Hadoop HDDS Checkstyle rule set used by Maven/build-time Java linting. It extends the standard Checkstyle `Checker`/`TreeWalker` model with HDDS-specific style, import, Javadoc, and code-quality constraints. It is not application runtime code; it defines static validation policy for Java sources in the Apache Ozone HDDS tree.

## Important modules and APIs
- Root module: `Checker`, using Checkstyle DTD `configuration_1_2.dtd`.
- File-level modules: `Header`, `BeforeExecutionExclusionFileFilter`, `SuppressWarningsFilter`, `JavadocPackage`, `NewlineAtEndOfFile`, `Translation`, `FileTabCharacter`, `LineLength`, and `RegexpMultiline`.
- AST modules under `TreeWalker`: `SuppressWarningsHolder`, suppression comment filters, Javadoc checks, naming checks, import checks, size checks, whitespace checks, modifier/block/coding/design checks, `ArrayTypeStyle`, `Indentation`, `UpperEll`, and `ModifierOrder`.
- HDDS-specific constraints include the license header path `hadoop-hdds/dev-support/checkstyle/license.header`, generated-source exclusion `.*/target/generated.*`, line length `120`, and a regex ban on `Preconditions.checkNotNull` in favor of `Objects.requireNonNull`.
- Import policy forbids `sun.*`, relocated/shaded packages, selected `org.apache.hadoop.test` utilities, and `org.apache.hadoop.fs.CommonConfigurationKeys`.

## Control flow
Checkstyle loads the root `Checker`, applies file-level filters and checks, then runs `TreeWalker` checks over Java ASTs. Generated files under `target/generated*` are filtered before execution. Suppression annotations/comments are enabled through `SuppressWarningsFilter`, `SuppressWarningsHolder`, `SuppressionCommentFilter`, and `SuppressWithNearbyCommentFilter`, so selected violations can be locally waived when Checkstyle is configured to honor them.

## State and persistence
The file has no mutable runtime state. Its persistent effect is policy: build runs and IDE integrations using this config will report or fail on violations. The only external file state it references directly is the required license header file.

## Dependencies and integration points
This integrates with Checkstyle, the HDDS Maven build, Java source files, generated-source directories, and any suppression configuration wired by the build. The DTD is referenced from `https://checkstyle.org/dtds/configuration_1_2.dtd`. The rule set assumes modern Checkstyle support for tokens such as `RECORD_DEF` and `COMPACT_CTOR_DEF`.

## Risks and edge cases
- The `Header` path is relative to the build execution layout; moving the module or changing Maven working directories can break header resolution.
- The `IllegalImport` regex is broad for relocated/shaded packages and can reject intentional internal relocation imports.
- `RegexpMultiline` searches across lines for `Preconditions.checkNotNull`; false positives are possible in comments or non-code text if file extension scoping changes.
- New Java language constructs require Checkstyle/token compatibility; the config already includes record tokens, but future constructs may need updates.
- Javadoc and package checks can produce high churn in generated, test, or legacy packages unless suppressions are kept aligned.

## Test signals
Primary validation is running the Checkstyle goal/profile used by the HDDS Maven build. Useful targeted signals are: a Java file without the license header should fail `Header`; a Java file with tabs should fail `FileTabCharacter`; a long Java code line over 120 characters should fail unless matching the ignore pattern; an import from `sun.*` or `*.shaded.*` should fail; `Preconditions.checkNotNull` should emit the configured replacement message; generated files under `target/generated*` should be excluded.
