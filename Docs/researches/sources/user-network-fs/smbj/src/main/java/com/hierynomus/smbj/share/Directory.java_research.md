<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/share/Directory.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/share/Directory.java

Purpose: Represents an open directory handle and provides directory enumeration plus change notification.

Important APIs/types/functions: list() and generic list(Class, String) collect iterator results. iterator(Class, String) returns DirectoryIterator. watchAsync(Set<SMB2CompletionFilter>, boolean) issues SMB2 CHANGE_NOTIFY through Share. getFileId() exposes the handle id.

Control flow: DirectoryIterator decodes using FileInformationFactory, sends an initial QUERY_DIRECTORY with SMB2_RESTART_SCANS, then repeatedly issues follow-up queries until STATUS_NO_MORE_FILES, STATUS_NO_SUCH_FILE, or an identical buffer is returned. next() consumes decoded information records from the current response buffer before requesting more.

State and persistence behavior: Directory handle state lives in Open/DiskEntry. Iterator keeps currentBuffer, currentIterator, decoder, searchPattern, and next item. No disk persistence.

Dependencies and integration points: Uses Share.queryDirectory(), FileInformationFactory decoders, SMB2QueryDirectory flags/statuses, and change notify APIs.

Risks: The identical-buffer macOS workaround can hide legitimate repeated directory pages if a server returns identical bytes with distinct semantic position. The iterator is not thread-safe and remove() is unsupported. Search pattern semantics depend on server implementation.

Test signals: Empty directory, no-match search pattern, multi-page listing, macOS duplicate-buffer EOF workaround, generic information classes, change notify watchTree flag, and close behavior inherited from DiskEntry.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/share/Directory.java -->
