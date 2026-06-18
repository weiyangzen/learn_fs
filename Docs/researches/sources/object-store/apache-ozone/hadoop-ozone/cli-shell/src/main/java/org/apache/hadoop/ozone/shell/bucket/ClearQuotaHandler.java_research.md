## sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/bucket/ClearQuotaHandler.java

Purpose: bucket `clrquota` command that clears space and/or namespace quota.

Important APIs and control flow: mixes in `ClearSpaceQuotaOptions`, resolves the target bucket through object store volume/bucket lookup, calls `clearSpaceQuota` and/or `clearNamespaceQuota` based on flags, and throws `IOException` if neither flag was supplied.

State and dependencies: persists quota changes through OM RPCs on `OzoneBucket`. Depends on `BucketHandler`, `ClearSpaceQuotaOptions`, and Ozone client model.

Risks and test signals: not atomic across both quota types if one call succeeds and the other fails. Validation is local for missing flags. No direct tests in this subset.
