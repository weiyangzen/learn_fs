<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/share/PrinterShare.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/share/PrinterShare.java

Purpose: Share subtype for printer shares, turning InputStream or ByteChunkProvider data into a temporary SMB open and writes.

Important APIs/types/functions: print(InputStream), print(InputStream, ProgressListener), print(ByteChunkProvider), and print(ByteChunkProvider, ProgressListener).

Control flow: print opens the printer share path with FILE_WRITE_DATA, FILE_ATTRIBUTE_NORMAL, FILE_SHARE_WRITE, FILE_CREATE, FILE_NON_DIRECTORY_FILE, and FILE_WRITE_THROUGH. It writes provider data using SMB2Writer and closes the file id in finally.

State and persistence behavior: No extra state beyond Share. Remote printer spool state changes as bytes are written.

Dependencies and integration points: Extends Share and uses InputStreamByteChunkProvider, SMB2Writer, AccessMask, create disposition/options, and ProgressListener.

Risks: FILE_CREATE may fail if the server expects a generated spool file name or if an entry exists. closeFileId in finally can throw and mask write failure. InputStreamByteChunkProvider ownership of closing the input is external.

Test signals: Input stream print, provider print, progress, close on write failure, access/create option expectations against a printer-capable server or mock share.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/share/PrinterShare.java -->
