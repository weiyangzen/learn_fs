## sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/bucket/DeleteBucketHandler.java

Purpose: bucket `delete` command, with optional recursive deletion for non-empty buckets.

Important APIs and control flow: resolves target volume/bucket and OM service ID. Non-recursive mode calls `vol.deleteBucket`. Recursive mode requires `-y/--yes` or an interactive `yes` confirmation, then branches by bucket layout. OBS buckets are listed and deleted in batches of 1000 keys before deleting the bucket. FSO/legacy buckets are deleted through the OFS `FileSystem.delete(path, true)` path using an `ofs://<service-id>/volume/bucket` URI.

State and dependencies: deletes keys and bucket metadata through OM/OFS clients; this is irreversible and bypasses trash for recursive deletes per prompt. Depends on Ozone client, Hadoop FS, OFS constants, and bucket layout.

Risks and test signals: broad destructive behavior; confirmation text warns no recovery. Error handling prints messages but does not rethrow in recursive helpers. No direct tests in this subset.
