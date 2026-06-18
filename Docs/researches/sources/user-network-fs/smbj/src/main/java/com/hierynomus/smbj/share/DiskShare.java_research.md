<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/share/DiskShare.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/share/DiskShare.java

Purpose: High-level disk-share API for opening files/directories, path-aware DFS/symlink resolution, existence checks, listing, mkdir/rm/rmdir, file/security/share/volume information, and deletion.

Important APIs/types/functions: open(), openDirectory(), openFile(), fileExists(), folderExists(), list() overloads, mkdir(), get/setFileInformation() by path or fileId, getShareInformation(), getVolumeInfo(), rmdir(), rm(), deleteOnClose(), get/setSecurityInfo(). createFileAndResolve() and resolveAndCreateFile() connect PathResolver to SMB2 CREATE and reroute to nested sessions/shares.

Control flow: Public open builds SmbPath then proactively resolves and creates. CREATE responses can trigger reactive resolver flow; rerouteIfNeeded switches session/share for DFS targets. getDiskEntry chooses Directory when FILE_ATTRIBUTE_DIRECTORY is set. Recursive rmdir lists children, skips dot entries, recurses directories, removes files, then marks directory delete-on-close.

State and persistence behavior: Holds a PathResolver. All data operations mutate remote SMB filesystem state. No local persistence.

Dependencies and integration points: Extends Share, uses Session.getNestedSession(), PathResolver, SmbPath, file information factories, security descriptors, and SMB2 create/query/set constants.

Risks: Recursive rmdir has no cycle protection for reparse points or DFS/symlink paths. exists() returns false for several status codes but rethrows others. Casting rerouted share to DiskShare assumes target share type. Root path deletion is rejected only for null/empty rmdir. Open resolution recursion needs tests for loops.

Test signals: DFS and symlink create reroute, openFile/openDirectory option normalization, existence status handling, list generic classes, mkdir, share/volume info parsing, recursive delete with mixed entries, delete pending idempotence, security SACL access mask, and file info codecs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/share/DiskShare.java -->
