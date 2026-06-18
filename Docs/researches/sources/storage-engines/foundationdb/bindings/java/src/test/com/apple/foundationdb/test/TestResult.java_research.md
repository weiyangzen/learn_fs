# sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/TestResult.java

Purpose: lightweight result collector for Java performance tests, writing KPI and error data to a JSON-like file.

Important APIs and flow: constructor generates a random positive id, `addKpi` stores value and units under a name, `addError` records throwables, and `save` writes `javaresult-<id>.json` in the requested directory. Output is built manually with sorted KPI maps and escaped stack traces.

State and persistence: in-memory KPI/error maps become a filesystem artifact. Dependencies are standard Java IO and collections. Risks include manual JSON construction, partial escaping, no directory creation, random id collision possibility, and throwing on write failure after printing a message. Signal is the persisted result file consumed by benchmark automation or humans.
