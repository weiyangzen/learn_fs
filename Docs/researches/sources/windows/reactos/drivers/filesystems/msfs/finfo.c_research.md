# File Research: sources/windows/reactos/drivers/filesystems/msfs/finfo.c

This file implements mailslot query and set information dispatch.

`MsfsQueryMailslotInformation` fills `FILE_MAILSLOT_QUERY_INFORMATION` with max message size, read timeout, available message count, and next message size. If no message is queued, it reports `MAILSLOT_NO_MESSAGE` as `MAXULONG`.

`MsfsSetMailslotInformation` updates the FCB read timeout from `FILE_MAILSLOT_SET_INFORMATION`.

`MsfsQueryInformation` and `MsfsSetInformation` both require the caller to be the server side of the mailslot. Client-side callers receive `STATUS_ACCESS_DENIED`. Supported information classes are `FileMailslotQueryInformation` and `FileMailslotSetInformation`; other classes return `STATUS_NOT_IMPLEMENTED`.

Research notes:
- Buffer-size failures return `STATUS_BUFFER_OVERFLOW`.
- Query information length is reported as bytes consumed from the caller’s original buffer length.
- The file locally undefines and redefines mailslot constants to `MAXULONG`.
