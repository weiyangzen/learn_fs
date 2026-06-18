# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/Archiver.java

Purpose: `Archiver` creates and extracts tar archives for Ozone/HDDS file trees and checkpoint/container transfer workflows.

Important APIs/types/functions: `create(tarFile, from)` tars a directory tree. `extract(tarFile, dir)` untars into a target directory. `includePath()` recursively adds directories/files. `includeFile()` adds a single file. `linkAndIncludeFile()` hard-links a file into a temp dir before archiving and removes the link afterward. `extractEntry()` validates target paths and writes entries. `tar()`, `untar()`, `readEntry()`, and `getBufferSize()` provide archive stream helpers.

Control flow: tar creation opens a `TarArchiveOutputStream`, adds a directory entry before children, lists directory contents, and recursively writes files with size/mode/time metadata. Extraction opens a `TarArchiveInputStream`, resolves each entry under the destination, calls `HddsUtils.validatePath()` to prevent escaping the ancestor, creates directories, and copies file bytes with a bounded buffer.

State and persistence: stateless utility class. It reads/writes filesystem archives and preserves basic file timestamps. Tar output uses POSIX long-file and big-number modes.

Dependencies/integration: depends on Apache Commons Compress/IO, Hadoop/Ozone constants, `HddsUtils.validatePath`, and Java NIO. Used by container packers and DB checkpoint/snapshot transfer code.

Risks: `includePath()` constructs entry names with `subdir + "/" + fileName`, producing leading slash-like names when `subdir` is empty depending on path handling. Hard-link inclusion requires filesystem support and same-device semantics. Extraction safety depends on `validatePath()` handling malicious tar entries.

Test signals: `TestArchiver` covers buffer sizing and hard-link inclusion success/failure. Container packer tests exercise archive entry creation. DB checkpoint paths indirectly use archive streaming helpers.
