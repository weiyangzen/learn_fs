# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/fs/contract/AbstractContractCopyFromLocalTest.java

Purpose: `AbstractContractCopyFromLocalTest` validates `FileSystem.copyFromLocalFile` behavior for files, directories, overwrite, delete-source, missing source, and file/directory conflicts. It bridges local Java temp files with the remote test filesystem.

Important APIs/types/functions: extends `AbstractFSContractTestBase`; uses `java.io.File`, `java.nio.file.Files`, Commons IO `FileUtils`/`IOUtils`, Hadoop `FileSystem`, `Path`, `FileStatus`, `PathExistsException`, and `FileAlreadyExistsException`. Helpers include `copyFromLocal(File, overwrite, delSrc)`, `fileToPath`, temp file/directory builders, and `assertFileTextEquals`.

Control flow: `teardown()` deletes the tracked temp file. Simple file tests create temp files, copy them to `path(srcFile.getName())`, verify existence, length, and ASCII text, then check overwrite/no-overwrite behavior. Missing-source and `delSrc` tests assert local-side deletion or `FileNotFoundException`. Directory tests create temp directory trees, call `copyFromLocalFile`, and verify remote directory and child paths using relative local paths. Conflict tests ensure copying a directory over a file fails.

State and persistence behavior: state exists in both local temp storage and the target filesystem. The tests assert remote content persistence, source preservation by default, source deletion when `delSrc` is true, directory recursion, and overwrite replacing previous remote file contents.

Dependencies and integration points: this class exercises Hadoop's local-to-filesystem copy path, so it integrates local file URI resolution, remote `mkdirs`, remote create, and remote open/read. The destination naming scheme maps local filenames into the contract test root.

Risks and test signals: catches implementations that delete sources when not requested, ignore overwrite flags, flatten directory trees incorrectly, mishandle empty directories, accept missing sources, or allow directory-to-file copies. Some helper logic depends on temp filenames, so failures can be sensitive to local filesystem path normalization.
