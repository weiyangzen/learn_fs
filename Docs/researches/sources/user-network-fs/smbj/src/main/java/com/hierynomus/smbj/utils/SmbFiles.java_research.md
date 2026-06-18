<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/utils/SmbFiles.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/utils/SmbFiles.java

Purpose: Convenience utilities for copying local data to an SMB DiskShare and recursively creating remote directories.

Important APIs/types/functions: static copy(File, DiskShare, String, boolean), static write(InputStream, DiskShare, String, boolean), mkdirs(DiskShare, String), and mkdirs(DiskShare, SmbPath).

Control flow: copy validates source exists/readable/isFile, opens a FileInputStream, and delegates to write. write opens the destination with GENERIC_WRITE, FILE_ATTRIBUTE_NORMAL, FILE_SHARE_WRITE, create disposition FILE_OVERWRITE_IF or FILE_CREATE, then writes an InputStreamByteChunkProvider. mkdirs checks folderExists for the path, recurses to parent, then mkdirs the current path.

State and persistence behavior: Stateless local utility; mutates remote share filesystem. copy closes local input and remote file through try-with-resources.

Dependencies and integration points: Uses DiskShare.openFile(), File.write(), SmbPath parents, and SMB2 create constants.

Risks: copy silently returns 0 for missing/unreadable/non-file source. write silently returns 0 for null source or destPath. mkdirs recursion depends on SmbPath.getParent() terminating; root/empty path behavior needs coverage. Access/share flags may be too restrictive for concurrent readers.

Test signals: Copy success byte count, missing source returns zero, overwrite true/false dispositions, write null arguments, mkdirs nested creation, mkdirs existing path, and root parent termination.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/utils/SmbFiles.java -->
