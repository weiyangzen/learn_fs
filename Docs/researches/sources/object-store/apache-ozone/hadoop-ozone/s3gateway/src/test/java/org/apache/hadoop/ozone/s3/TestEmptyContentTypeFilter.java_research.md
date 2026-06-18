
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/TestEmptyContentTypeFilter.java

Purpose: tests `EmptyContentTypeFilter.EnumerationWrapper`, the helper used by the servlet filter that removes empty `Content-Type` header entries.

Important APIs and control flow: first test feeds an enumeration containing `Content-Type`, `1`, `2`, `Content-Type` and asserts only `1` and `2` are returned. Second test feeds only `Content-Type` and asserts the wrapper is empty.

State, dependencies, integration: uses `Vector` enumerations and the nested wrapper class. Integration point is the `optional-content-type` filter configured in main `web.xml`.

Risks and test signals: covers enumeration behavior only, not full servlet request wrapping. It assumes exact string matching for `Content-Type`.
