<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen_develop.yml -->
# sources/storage-engines/wiredtiger/test/evergreen_develop.yml

Purpose: Evergreen overlay for the WiredTiger develop project. It includes `test/evergreen.yml` and adds develop-only variants for performance, documentation, code statistics, compatibility, infrequent, and LazyFS testing.

Important structures: `perf-tasks-template` defines batchtime, common perf expansions such as TCMalloc, release build type, doubled CPU job count, database name, and a set of perf task selectors. Build variants instantiate this for Ubuntu x86 and Amazon ARM64. `documentation-update` runs weekly doc update tasks across maintained branches. `code-statistics` runs split coverage, coverage merge, catch2 coverage, cyclomatic complexity, code-change report, and modularity metrics. Compatibility, memory-model, and LazyFS variants configure their own task lists and expansions.

State and persistence: declarative YAML only; runtime state is produced by included tasks/functions.

Dependencies and integration: relies on anchors/tasks/functions from included `test/evergreen.yml` and on variant-specific distros. It activates coverage per-test only manually.

Risks and test signals: changes here affect scheduling and build-variant coverage rather than code behavior. Perf tasks use long batch times and disabled stepback for infrequent checks. Missing include anchors or renamed tasks in base Evergreen config will break validation.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen_develop.yml -->
