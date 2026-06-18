## sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/SetSpaceQuotaOptions.java

Purpose: reusable picocli mixin for space and namespace quota-setting commands.

Important APIs and control flow: defines `--space-quota` with backward-compatible alias `--quota`, and `--namespace-quota`. Getters return raw strings so consumers can parse them with `OzoneQuota`.

State and dependencies: parse-time state only. Depends on picocli.

Risks and test signals: validation is intentionally deferred to callers, so command handlers must enforce at least one option and parse units/counts. `CreateBucketHandler` and `SetQuotaHandler` consume this mixin.
