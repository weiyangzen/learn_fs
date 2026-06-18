## sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/ListLimitOptions.java

Purpose: reusable mutually exclusive list-length options for shell list commands.

Important APIs and control flow: picocli `@ArgGroup` contains `--length`/`-l` with default 100 and `--all`/`-a`. `getLimit` returns `Integer.MAX_VALUE` for all mode and rejects non-positive lengths. `isAll` exposes the all flag.

State and dependencies: parse-time state only. Depends on picocli argument-group semantics to keep the options exclusive.

Risks and test signals: returning `Integer.MAX_VALUE` pushes memory/latency risk to handlers that materialize results. No direct tests in this subset.
