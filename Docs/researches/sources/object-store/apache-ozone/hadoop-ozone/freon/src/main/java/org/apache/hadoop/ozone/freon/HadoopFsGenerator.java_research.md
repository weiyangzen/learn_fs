## sources/object-store/apache-ozone/hadoop-ozone/freon/src/main/java/org/apache/hadoop/ozone/freon/HadoopFsGenerator.java

Purpose: Freon subcommand `dfsg`/`dfs-file-generator` that creates random files through any Hadoop-compatible filesystem.

Important APIs/types/functions: options configure file size, content buffer size, copy-buffer size, and sync option (`NONE`, `HFLUSH`, `HSYNC`). `call` initializes FS and content generator; `createFile` writes each generated file.

Control flow: initialize base FS, create parent directory for object zero, build `ContentGenerator`, create timer, then run tests. Each task constructs `<root>/<prefix>/<counter>`, creates the file, writes generated content, and closes the stream.

State and persistence behavior: creates files under the configured root path. Local state is content generator and timer.

Dependencies and integration points: extends `HadoopBaseFreonGenerator`, uses Hadoop `FileSystem` and `FSDataOutputStream`.

Risks: static `flushOrSync` option is shared across instances in a JVM; parent directory is only proactively created for object zero but the path schema is shallow so this is enough by default; overwrite behavior depends on FS create semantics.

Test signals: pair with `HadoopFsValidator`; check file creation count and sync behavior on Syncable streams.
