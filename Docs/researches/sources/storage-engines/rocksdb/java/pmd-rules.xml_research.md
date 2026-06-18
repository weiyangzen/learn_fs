<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/pmd-rules.xml -->
# Research: sources/storage-engines/rocksdb/java/pmd-rules.xml

Purpose: Defines a custom PMD ruleset for RocksDB Java code, enabling broad PMD categories while carving out exceptions that match the JNI-heavy API style.

Important APIs/types/functions: The ruleset references `category/java/codestyle.xml`, `category/java/errorprone.xml`, `AvoidLiteralsInIfCondition`, `category/java/bestpractices.xml`, and `CloseResource`. It configures excluded rule names, ignored magic numbers/expressions, close-resource types, allowed resource types, and finally behavior.

Control flow: PMD loads the ruleset, applies the referenced categories, removes excluded checks, and uses custom properties for literal and resource-close detection. The Java Makefile target `pmd` invokes Maven PMD/CPD/check phases.

State and persistence behavior: This file does not persist runtime state. It controls static-analysis pass/fail behavior and generated PMD reports.

Dependencies and integration points: Depends on PMD ruleset schema, Maven PMD plugin configuration, and the Java source tree. It is intentionally permissive around native code, naming, short variables, and resource patterns common in JNI wrappers.

Risks and edge cases: Broad exclusions can hide maintainability issues indefinitely. Allowed resource types and close-resource configuration must stay synchronized with RocksDB wrapper ownership conventions. The description contains a typo but does not affect parsing.

Test signals: `make -C java pmd` or Maven PMD checks should parse this ruleset and report only accepted findings. Adding a deliberately unclosed non-allowed resource should still fail.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/pmd-rules.xml -->
