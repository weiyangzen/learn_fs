<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/handlers/DirectoryEntityHandler.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/handlers/DirectoryEntityHandler.java

## Purpose

`DirectoryEntityHandler` handles namespace APIs for directory-level paths in FSO or legacy filesystem-style buckets.

## Important APIs and Types

It returns directory `ObjectDBInfo`, recursive `CountStats`, `DUResponse`, type-not-applicable quota, and file-size distributions.

## Control Flow

Summary resolves the directory object id through the bucket handler, counts descendant directories and files, and maps directory metadata. DU reads the directory NSSummary, emits child-directory rows, optionally appends direct keys, sorts rows, and sets direct key size plus optional replicated size. Distribution recursively accumulates from the directory object id.

## State and Persistence

No writes occur. Reads come from namespace summary, OM directory/key tables through bucket handlers, and OM metadata managers.

## Dependencies and Integration Points

It depends on `BucketHandler` for object-id lookup and direct-key enumeration. `NSSummaryEndpoint` invokes it after `EntityHandler` classifies a path as `DIRECTORY`.

## Risks and Edge Cases

Missing directory NSSummary is treated as an empty directory. Child NSSummary rows are dereferenced without null checks. `Paths.get(dirName).getFileName()` can be null and is converted to an explicit `NullPointerException`. Quota is not applicable for directories.

## Test Signals

Tests should cover empty directories, nested child directories, direct files, replica DU, sorted and unsorted responses, file-size distribution, missing child summaries, and layout-specific directory object ids.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/handlers/DirectoryEntityHandler.java -->
