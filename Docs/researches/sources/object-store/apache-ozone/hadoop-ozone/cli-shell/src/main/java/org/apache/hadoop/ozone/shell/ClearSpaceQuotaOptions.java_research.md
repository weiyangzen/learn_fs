## sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/ClearSpaceQuotaOptions.java

Purpose: reusable picocli mixin for bucket/volume quota-clear commands.

Important APIs and control flow: defines boolean options `--space-quota` and `--namespace-quota`, with getters `getClrSpaceQuota` and `getClrNamespaceQuota`. Consumers decide whether at least one flag is required.

State and dependencies: no persistence; picocli populates booleans from CLI parsing. Depends only on picocli.

Risks and test signals: this class does not enforce "at least one" itself; callers such as `ClearQuotaHandler` must perform that validation. No direct tests in this subset.
