## sources/object-store/apache-ozone/hadoop-ozone/freon/src/main/java/org/apache/hadoop/ozone/freon/HadoopBaseFreonGenerator.java

Purpose: base class for Freon commands that operate through Hadoop `FileSystem`.

Important APIs/types/functions: option `--rpath/--path` sets a root Hadoop FS URI, default `o3fs://bucket1.vol1`. `init` captures Ozone configuration, parses URI, disables FS cache for the scheme, and delegates to base init. `getFileSystem` returns a thread-local FileSystem. `taskLoopCompleted` closes the thread-local FS.

Control flow: subclasses call `super.init`, then use `getRootPath` and `getFileSystem` in task providers. Each Freon worker thread lazily gets its own FileSystem instance.

State and persistence behavior: thread-local FileSystem clients and configuration are local. Persistent effects are filesystem operations performed by subclasses.

Dependencies and integration points: base for `HadoopFsGenerator`, `HadoopFsValidator`, `HadoopNestedDirGenerator`, and `HadoopDirTreeGenerator`.

Risks: `taskLoopCompleted` only closes the FileSystem for threads that reached it; `ThreadLocal` is not removed; disabling cache mutates local config and may surprise callers sharing it.

Test signals: verify per-thread FS creation, cache-disable key, and FS close after task loop.
