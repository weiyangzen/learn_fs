## sources/object-store/apache-ozone/hadoop-ozone/freon/src/main/java/org/apache/hadoop/ozone/freon/HadoopDirTreeGenerator.java

Purpose: Freon subcommand `dtsg`/`dfs-tree-generator` that creates a recursive directory tree and files through Hadoop FS.

Important APIs/types/functions: options configure depth, file count per directory, file size, buffer size, child span, and random name length. Methods include `call`, `createDir`, `createSubDirRecursively`, `makeDirWithGivenNumberOfFiles`, `createFile`, and `createFiles`.

Control flow: validates depth and span, initializes base FS, creates a `ContentGenerator`, starts timer, and runs `createDir` for each test. Each root creates one random directory with files, then recursively creates depth/span child directories, each populated with files.

State and persistence behavior: creates directories and files under the configured root path. Local `AtomicLong totalDirsCnt` and timer track counts.

Dependencies and integration points: extends `HadoopBaseFreonGenerator`, uses Hadoop `FileSystem`, `Path`, `FSDataOutputStream`, `ContentGenerator`, and metrics.

Risks: one Freon task can create many directories/files, so `--number-of-tests` multiplies quickly; random names make repeat cleanup harder; invalid options only print messages and return success.

Test signals: small depth/span/file-count runs should produce expected directory and file counts and timer increments.
