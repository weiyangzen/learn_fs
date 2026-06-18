# sources/storage-engines/foundationdb/bindings/java/fdb-java-style.xml

## Purpose
`fdb-java-style.xml` is the Checkstyle configuration for FoundationDB Java binding source. It defines formatting, naming, import, block, whitespace, and small design constraints intended to keep Java binding code idiomatic while still visually compatible with the wider FoundationDB codebase.

## Important APIs, Types, and Functions
The file configures Checkstyle's `Checker` root with a `SuppressionFilter` sourced from `suppressions.xml` and a `TreeWalker` containing modules such as `AvoidNestedBlocks`, `EmptyBlock`, `LeftCurly`, `HideUtilityClassConstructor`, `CovariantEquals`, `FallThrough`, `CustomImportOrder`, `AvoidStarImport`, `UnusedImports`, `Indentation`, `ModifierOrder`, naming checks, and whitespace checks.

## Control Flow
Checkstyle loads the DTD-backed XML, applies the suppression filter first, then walks Java ASTs under `TreeWalker`. Modules either enforce structural rules, report source formatting violations, or allow exceptions via explicit properties such as catch parameter naming and custom import ordering.

## State and Persistence Behavior
The file has no runtime state. Its persistent effect is build-time policy: any Maven or CI step invoking Checkstyle with this config will accept, reject, or suppress Java binding source style violations.

## Dependencies and Integration Points
It depends on Checkstyle's `configuration_1_3.dtd` schema and module names available in the configured Checkstyle version. It also depends on `suppressions.xml` being present relative to the Checkstyle invocation. It integrates with the Java binding build and review workflow rather than with runtime code.

## Risks and Edge Cases
The configuration references legacy Checkstyle module/property names; upgrades can break builds if modules are renamed or properties change. Some useful checks are commented out, including `DesignForExtension`, `FinalClass`, and `MagicNumber`, so the file is not a complete quality gate. The `CustomImportOrder` only defines three broad groups and may miss project-specific import grouping expectations.

## Test Signals
The primary signal is Checkstyle execution in Maven/CI. Passing tests show source syntax and style compatibility with this configuration, but not runtime correctness.
