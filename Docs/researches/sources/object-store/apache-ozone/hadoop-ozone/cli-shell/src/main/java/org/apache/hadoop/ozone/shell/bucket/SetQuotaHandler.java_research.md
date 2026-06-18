## sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/bucket/SetQuotaHandler.java

Purpose: bucket `setquota` command for changing bucket space and/or namespace quotas.

Important APIs and control flow: mixes in `SetSpaceQuotaOptions`, loads current bucket quotas, overrides provided values after parsing with `OzoneQuota`, requires at least one quota option, warns for buckets with old quota defaults suggesting inaccurate usage metrics, and calls `bucket.setQuota`.

State and dependencies: persists quota metadata through OM RPC. Depends on `OzoneQuota`, `OLD_QUOTA_DEFAULT`, and Ozone bucket APIs.

Risks and test signals: updates both quota values in one `OzoneQuota` object using existing values for omitted dimensions. Warning does not block old buckets. No direct tests in this subset.
