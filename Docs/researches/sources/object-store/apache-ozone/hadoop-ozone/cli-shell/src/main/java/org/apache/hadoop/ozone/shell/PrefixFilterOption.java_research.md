## sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/PrefixFilterOption.java

Purpose: reusable `--prefix`/`-p` option mixin for list commands.

Important APIs and control flow: stores a parsed prefix string and exposes it through `getPrefix`. Consumers pass the value to client list APIs.

State and dependencies: parse-time state only. Depends on picocli.

Risks and test signals: this class performs no normalization, escaping, or empty-string handling; semantics are defined by the consuming list API. `ListBucketHandler` consumes it in this subset.
