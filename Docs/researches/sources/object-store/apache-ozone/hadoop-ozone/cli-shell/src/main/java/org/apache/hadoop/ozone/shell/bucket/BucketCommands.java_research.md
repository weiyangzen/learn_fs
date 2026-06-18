## sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/bucket/BucketCommands.java

Purpose: command group for bucket-specific Ozone shell operations.

Important APIs and control flow: picocli command `bucket` registers info, list, create, set quota, link, delete, ACL operations, clear quota, set replication config, update, and hidden set-encryption-key handlers. It enables standard help and version provider.

State and dependencies: no direct state; public command surface metadata only. Depends on all registered handler classes and picocli.

Risks and test signals: this subcommand list controls user-facing availability. `UpdateBucketHandler` is referenced but outside this work item, so integration depends on that class compiling in the module.
