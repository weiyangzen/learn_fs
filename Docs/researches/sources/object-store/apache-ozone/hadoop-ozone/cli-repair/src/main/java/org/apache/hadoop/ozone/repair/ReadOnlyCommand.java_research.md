# sources/object-store/apache-ozone/hadoop-ozone/cli-repair/src/main/java/org/apache/hadoop/ozone/repair/ReadOnlyCommand.java

Purpose: `ReadOnlyCommand` is a marker interface for repair subcommands that do not modify state.

Important APIs and types: It declares no methods.

Control flow and state: None.

Dependencies and integration points: Repair command infrastructure or documentation can use this marker to distinguish diagnostic/read-only tools from mutating repair tools.

Risks and test signals: The risk is semantic drift if mutating commands implement it or read-only commands omit it. Tests are usually indirect through command classification.
