## sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/ListPaginationOptions.java

Purpose: reusable list pagination mixin combining list limit and start-after cursor.

Important APIs and control flow: mixes in `ListLimitOptions`, adds `--start`/`-s`, and exposes `getLimit`, `isAll`, and `getStartItem`. The start item is documented as excluded from results.

State and dependencies: parse-time state only; no persistence. Depends on `ListLimitOptions` and picocli mixin injection.

Risks and test signals: handlers must pass `startItem` to the correct client API and avoid over-materializing results. `ListBucketHandler` is one consumer in this subset.
