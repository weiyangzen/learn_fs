# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/scanner/user/scanuser.h

User-mode scanner messaging header.

Key contents:
- Applies `#pragma pack(1)` for message structures.
- Defines `SCANNER_MESSAGE`:
  - `FILTER_MESSAGE_HEADER MessageHeader`
  - `SCANNER_NOTIFICATION Notification`
  - embedded `OVERLAPPED Ovlp`
- Defines `SCANNER_REPLY_MESSAGE`:
  - `FILTER_REPLY_HEADER ReplyHeader`
  - `SCANNER_REPLY Reply`

Important behavior:
- `SCANNER_MESSAGE` embeds `OVERLAPPED` for asynchronous `FilterGetMessage` calls but excludes it from the message length by passing `FIELD_OFFSET(SCANNER_MESSAGE, Ovlp)`.
- `SCANNER_REPLY_MESSAGE` wraps the scanner-specific reply in the required filter-manager reply header.

Dependencies and risks:
- Depends on `scanuk.h` for scanner payload structures and `fltuser.h` for filter-manager message headers.
- Packing affects structure layout; kernel/user communication must use the same expected header and payload sizes.
