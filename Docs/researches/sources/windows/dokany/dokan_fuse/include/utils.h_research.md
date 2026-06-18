# File Research: sources/windows/dokany/dokan_fuse/include/utils.h

Utility declarations and stat-to-Windows-find-data conversion template for Dokan FUSE.

Key contents:
- UTF-8/wide conversion declarations.
- Unix/FileTime conversion helpers.
- C++ string path helpers: `wchar_to_utf8_cstr`, `unixify`, `extract_file_name`, `extract_dir_name`.
- `convertStatlikeBuf` template:
  - maps directory mode to `FILE_ATTRIBUTE_DIRECTORY`, otherwise normal;
  - maps 64-bit size to high/low Windows fields;
  - converts ctime/atime/mtime to creation/access/write FILETIMEs;
  - marks files read-only when no write bits are set;
  - marks dotfiles hidden.

Role:
- Shared utility surface for converting FUSE stat-style data into Dokan/Win32 metadata.
