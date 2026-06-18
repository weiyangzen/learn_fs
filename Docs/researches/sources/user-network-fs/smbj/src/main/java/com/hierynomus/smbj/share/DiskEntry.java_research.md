<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/share/DiskEntry.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/share/DiskEntry.java

Purpose: Abstract base for disk file system opens, shared by File and Directory, adding metadata, security, rename, hardlink, IOCTL, flush, and delete-on-close helpers.

Important APIs/types/functions: getUncPath(), getPath(), getDiskShare(), getFileInformation(), setFileInformation(), get/setSecurityInformation(), rename(), createHardlink(), ioctl overloads, flush(), deleteOnClose(), equals/hashCode.

Control flow: Methods mostly delegate to DiskShare with this fileId. setSecurityInformation(SecurityDescriptor) derives SecurityInformation flags from descriptor owner/group/control bits. rename and hardlink use FileRenameInformation and FileLinkInformation via setInfo.

State and persistence behavior: Inherits fileId, name, and share from Open. Operations mutate remote file system metadata, not local persistent state.

Dependencies and integration points: Depends on msfscc file information structures, msdtyp SecurityDescriptor/SecurityInformation, SMB2FileId, DiskShare, and SmbPath.

Risks: setSecurityInformation infers flags and can omit an intended empty DACL/SACL if descriptor control bits are not set. equals uses class, path, and share, not fileId, so renamed handles and reopen behavior can be subtle. closeNoWait does not expose completion/failure.

Test signals: Metadata query/set for file and directory, security descriptor flag inference, rename replace/rootDirectory variants, hardlink replace variants, IOCTL overloads, flush, delete-on-close, equality after rename/reopen.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/share/DiskEntry.java -->
