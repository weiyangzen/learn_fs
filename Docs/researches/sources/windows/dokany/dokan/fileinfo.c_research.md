# File Research: sources/windows/dokany/dokan/fileinfo.c

Query-information dispatcher and conversion helpers for file metadata and alternate stream enumeration.

Key responsibilities:
- Converts `BY_HANDLE_FILE_INFORMATION` into NT file information structures:
  - `FILE_BASIC_INFORMATION`
  - `FILE_STANDARD_INFORMATION`
  - `FILE_POSITION_INFORMATION`
  - `FILE_INTERNAL_INFORMATION`
  - `FILE_ALL_INFORMATION`
  - `FILE_NAME_INFORMATION`
  - `FILE_ATTRIBUTE_TAG_INFORMATION`
  - `FILE_NETWORK_OPEN_INFORMATION`
  - `FILE_ID_INFORMATION`
- Aligns allocation size with Dokan volume options.
- Implements `DokanFillFindStreamData()` to append `FILE_STREAM_INFORMATION` entries from user `WIN32_FIND_STREAM_DATA`.
- Implements `DokanEndDispatchGetFileInformation()` to select the requested file information class and complete the event.
- Implements `DokanEndDispatchFindStreams()` to finalize stream entry offsets and validate buffer size.
- Implements `DispatchQueryInformation()` for `IRP_MJ_QUERY_INFORMATION`, including special handling for `FileStreamInformation`.

Important behavior:
- Unsupported classes such as alternate name and compression return `STATUS_NOT_IMPLEMENTED`; unknown classes return `STATUS_INVALID_PARAMETER`.
- `FileEaInformation` is treated as success with an empty EA size.
- `FileNameInformation` and `FileNormalizedNameInformation` copy the name from the driver event context.
- `FileStreamInformation` is dispatched to `FindStreams` instead of `GetFileInformation`.
- Event result `BufferLength` is computed from the requested buffer length minus remaining space.

Dependencies:
- Uses `DOKAN_OPERATIONS.GetFileInformation` and optionally `FindStreams`.
- Uses `CreateDispatchCommon()` and `EventCompletion()` from `dokan.c`.
- Uses `ALIGN_ALLOCATION_SIZE()` and `IOEVENT_RESULT_BUFFER_SIZE()`.
- Depends on Windows NT information structure layouts and stream alignment requirements.

Notable risks:
- If user `GetFileInformation` fails, this code maps the result to `STATUS_INVALID_PARAMETER` instead of preserving the original status.
- `DokanFillFindStreamData()` uses the current buffer tail and `NextEntryOffset` protocol carefully; malformed internal state would corrupt stream enumeration.
- `DokanEndDispatchFindStreams()` assumes there is at least a `FILE_STREAM_INFORMATION` entry in the result buffer when finalizing offsets.
- Buffer overflow handling is present, but several helper calls inside `DokanFillFileAllInfo()` ignore intermediate status because a full `FILE_ALL_INFORMATION` size check is done first.
