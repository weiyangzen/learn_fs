# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/TestOMDBArchiver.java

Purpose: Tests `OMDBArchiver`, the component that records files and emits OM DB checkpoint archives with hardlink metadata. It validates both individual hardlink recording and full tar archive generation.

Important APIs and types: `OMDBArchiver`, `recordFileEntry`, `recordHardLinkMapping`, `writeToArchive`, `OM_HARDLINK_FILE`, `OZONE_RATIS_SNAPSHOT_COMPLETE_FLAG_NAME`, Hadoop `FileUtil.unTar`, `IOUtils.getINode`, `OzoneConfiguration`, and temp filesystem paths.

Control flow: `testRecordFileEntry` creates a dummy file, asks the archiver to record it under a hardlink entry name, then checks that the stored file is a different path with the same inode. `testWriteToArchive` parameterizes completion state, adds ten files and hardlink mappings, writes the archive to an output stream, untars it, and verifies file content and optional completion marker files.

State and persistence: all behavior is filesystem-backed. The archiver maintains an in-memory map of tar entry names to files plus a temp directory. Completed archives persist an OM hardlink mapping file and a Ratis snapshot complete marker; incomplete archives contain only recorded files.

Dependencies and integration points: integrates with snapshot checkpoint transfer code that later consumes hardlink maps, with Hadoop tar utilities, and with filesystem inode semantics. It assumes the test filesystem supports hardlinks and stable inode comparison.

Risks and edge cases: hardlink creation may be platform-sensitive; archive completeness depends on writing marker files only after successful completion; hardlink mappings must be relative and extractable; tar output must not omit non-empty files.

Test signals: non-empty tar output, exact extracted file counts, byte-for-byte dummy content, inode equality for hardlinks, and marker presence only when `completed` is true.
