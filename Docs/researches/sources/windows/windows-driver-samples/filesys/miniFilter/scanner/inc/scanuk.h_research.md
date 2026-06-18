# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/scanner/inc/scanuk.h

Shared scanner kernel/user communication header.

Key contents:
- Defines communication port name `\\ScannerPort`.
- Sets `SCANNER_READ_BUFFER_SIZE` to 1024 bytes.
- Defines `SCANNER_NOTIFICATION`, containing `BytesToScan`, padding/reserved space, and a 1024-byte `Contents` buffer.
- Defines `SCANNER_REPLY`, containing `BOOLEAN SafeToOpen`.

Important behavior:
- The kernel sends `SCANNER_NOTIFICATION` to user mode and expects `SCANNER_REPLY` indicating whether the content is safe.
- The fixed 1024-byte payload bounds both file-start scanning and write-buffer scanning.

Dependencies and risks:
- This is an ABI header shared by both `scanner.sys` and `scanuser.exe`; field layout and packing expectations must remain synchronized.
- The port-name definition is included in separate kernel/user binaries, so duplicate definition is not an issue in this sample layout.
