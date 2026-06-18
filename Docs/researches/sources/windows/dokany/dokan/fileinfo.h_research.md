# File Research: sources/windows/dokany/dokan/fileinfo.h

Defines Windows NT file-system interface constants and structures used by Dokan user-mode dispatch code.

Key contents:
- IRP major/minor constants for create, read, write, query/set information, volume information, security, lock, cleanup, and PnP style operations.
- `FILE_INFORMATION_CLASS` and `FS_INFORMATION_CLASS` enums mirroring Windows kernel information classes.
- Struct definitions for file metadata, directory enumeration, rename/link/disposition, streams, volume labels, size/attribute info, network open info, and `UNICODE_STRING`.
- Flexible trailing array structs such as `FILE_NAME_INFORMATION`, `FILE_DIRECTORY_INFORMATION`, `FILE_RENAME_INFORMATION`, and volume/file-system name records.
- Alignment helpers: `ALIGN_DOWN`, `ALIGN_UP`, pointer alignment variants, word/long/quad alignment, and quad-alignment check.
- Create/open disposition and option flag constants copied from WDM-style definitions.
- Delete disposition flags, including POSIX semantics and on-close behavior.

Important behavior:
- This is a compatibility contract header, not executable logic.
- Many structures are consumed by `setfile.c`, `volume.c`, and other dispatchers to interpret buffers coming from the Dokan driver.
- Several definitions overlap Windows SDK/DDK types, allowing Dokan’s user-mode component to compile with the needed NT structures available.

Risks and notes:
- Many structs use one-element trailing arrays and require careful buffer-length accounting by callers.
- The file intentionally redefines low-level NT concepts; mismatches with newer Windows headers would affect ABI interpretation.
