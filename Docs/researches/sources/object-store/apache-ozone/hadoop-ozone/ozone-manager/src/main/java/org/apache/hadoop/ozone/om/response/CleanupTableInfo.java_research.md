# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/CleanupTableInfo.java

Purpose: `CleanupTableInfo` is a runtime annotation used on `OMClientResponse` classes to declare which OM metadata tables are affected and therefore eligible for cache cleanup after response processing.

Important APIs and types: It is `@Retention(RUNTIME)`, `@Target(TYPE)`, `@Inherited`, and exposes `cleanupTables()` plus `cleanupAll()`.

Control flow: Response classes annotate themselves with table constants from `OMDBDefinition`. Cleanup infrastructure can inspect annotations and clear affected caches without hard-coding every response class.

State and persistence behavior: The annotation itself stores metadata only. It does not mutate DB state, but incorrect metadata can leave stale table-cache entries.

Dependencies and integration points: It integrates response classes, OM table definitions, and cache-cleanup mechanisms.

Risks and test signals: Tests should verify every mutating response declares all affected tables, `cleanupAll` is mutually understood with an empty table list, and inherited annotations behave as intended for subclasses.
