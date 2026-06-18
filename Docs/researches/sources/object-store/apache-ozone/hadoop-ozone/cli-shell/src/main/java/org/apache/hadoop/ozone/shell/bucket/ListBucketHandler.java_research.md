## sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/bucket/ListBucketHandler.java

Purpose: bucket `list`/`ls` command for listing buckets in a volume.

Important APIs and control flow: extends `VolumeHandler` and mixes in pagination and prefix filter options plus `--has-snapshot`. It resolves the volume, calls `vol.listBuckets(prefix, start, filterByHasSnapshot)`, copies up to the requested limit into a list, wrapping link buckets in `InfoBucketHandler.LinkBucket`, then prints JSON array output. Verbose mode prints a count to stderr.

State and dependencies: read-only metadata listing. Depends on Ozone client volume APIs, `ListPaginationOptions`, `PrefixFilterOption`, and link-bucket wrapper.

Risks and test signals: results are materialized into memory up to limit; `--all` can be large. Pagination semantics depend on server-side start-item handling. No direct tests in this subset.
