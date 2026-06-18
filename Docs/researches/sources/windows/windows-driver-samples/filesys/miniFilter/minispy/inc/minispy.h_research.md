# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/minispy/inc/minispy.h

Shared kernel/user ABI header for MiniSpy.

Key contents:
- Defines MiniSpy-specific FltMgr pseudo-major codes for FSFilter, Fast I/O, volume mount/dismount, and transaction notification logging.
- Defines MiniSpy version `2.0` and communication port name `\\MiniSpyPort`.
- Defines shared scalar aliases, including `FILE_ID` and user-visible `NTSTATUS`.
- Sets fixed record transport size to `RECORD_SIZE` = 1024 bytes.
- Defines record types and flags for normal records, file-tag records, static fallback records, memory-limit records, and out-of-memory records.
- Defines `RECORD_DATA`, the fixed metadata captured for each callback: times, object IDs, process/thread IDs, status/information, flags, callback major/minor IDs, six generic arguments, and ECP summary fields.
- Defines variable-length `LOG_RECORD` and enclosing `RECORD_LIST`.
- Defines `MINISPY_COMMAND` and `COMMAND_MESSAGE` for user/kernel commands.

Important behavior:
- `LOG_RECORD.Name[]` is a flexible trailing string area and is packed into the 1024-byte transport record.
- `MAX_NAME_SPACE`, `MAX_NAME_SPACE_LESS_NULL`, `MAX_NAME_WCHARS_LESS_NULL`, and `MAX_LOG_RECORD_LENGTH` keep names aligned and bounded.
- Helper macros `Add2Ptr`, `ROUND_TO_SIZE`, and `FlagOn` are provided when not already present.

Dependencies and risks:
- This file is the contract between `minispy.sys` and `minispy.exe`; layout, alignment, and record-size changes must be coordinated on both sides.
- Several callback major IDs are negative `UCHAR` values, so consumers must treat them consistently with MiniSpy’s definitions rather than standard IRP major-code ranges alone.
