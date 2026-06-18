# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/stream/DirectoryServerSource.java

Purpose: implements `StreamingSource` by walking a subdirectory under a root and returning all regular files for streaming.

Important APIs and functions: `getFilesToStream(String id)` resolves `root/id`, walks the tree with `Files.walk`, filters regular files, and maps each file's logical name to `root.relativize(path).toString()`. IO failures are wrapped in `StreamingException`.

Control flow and state: state is only the root path. The returned map has no defined ordering because it is a `HashMap`.

Dependencies and integration: consumed by `DirstreamServerHandler`, which turns the returned map into a list and streams each entry.

Risks and test signals: nondeterministic order may affect reproducibility, and invalid IDs may escape root if not sanitized. Tests should cover recursive files, empty directories, symlinks according to `Files.walk` behavior, IO errors, interrupted signature compatibility, and path traversal.
