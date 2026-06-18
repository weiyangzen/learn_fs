
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/TestOzoneClientCache.java

Purpose: tests failure behavior of `OzoneClientCache.initialize`.

Important APIs and control flow: one test enables security and clears OM address, expecting `IOException`. Another configures multiple OM service IDs without an internal service ID and asserts the error mentions multiple service IDs. The third sets internal service ID with multiple service IDs and asserts initialization still fails for incomplete config but not for the multiple-service-ID validation.

State, dependencies, integration: each test creates a new `OzoneConfiguration` and `OzoneClientCache`. Integration point is endpoint/client initialization code that builds Ozone clients from config.

Risks and test signals: failure-only tests do not verify successful client caching or close behavior. They protect user-facing diagnostics for ambiguous HA service ID config.
