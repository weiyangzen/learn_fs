## sources/object-store/apache-ozone/hadoop-ozone/freon/src/main/java/org/apache/hadoop/ozone/freon/HadoopNestedDirGenerator.java

Purpose: Freon subcommand `ddsg`/`dfs-directory-generator` that creates nested directory paths through Hadoop FS.

Important APIs/types/functions: options configure depth, span of child directories under the leaf, and random name length. `call` validates options and runs `createDir`.

Control flow: for each task, generate a random path of `depth` segments, call `mkdirs` on the parent path, derive a leaf prefix, then create `span` sibling/child paths by appending numeric names and `/0`.

State and persistence behavior: creates directory metadata under the configured FS root. No file content is written.

Dependencies and integration points: extends `HadoopBaseFreonGenerator`, uses commons random strings and Hadoop `Path`.

Risks: string slicing for `leafDir` assumes name length and trailing segment layout; invalid depth/span prints and exits without failing; random paths are not reproducible.

Test signals: small depth/span run should create expected directory structure under the root path.
