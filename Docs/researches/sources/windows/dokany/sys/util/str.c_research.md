# File Research: sources/windows/dokany/sys/util/str.c

## Purpose
Implements Dokany kernel-mode Unicode string helpers for allocation, duplication, prefix checks/replacement, mount-point classification, and simple character search.

## Main Behavior
- Defines global prefix constants:
  - `g_DosDevicesPrefix` as `\DosDevices\`
  - `g_VolumeGuidPrefix` as `\??\Volume{`
  - `g_ObjectManagerPrefix` as `\??\`
- `DokanAllocateUnicodeString()` allocates a `UNICODE_STRING` plus copied null-terminated buffer, validates with `RtlUnicodeStringInitEx`, and frees on failure.
- `DokanFreeUnicodeString()` frees both the buffer and wrapper struct.
- `DokanAllocDuplicateString()` and `DokanDuplicateUnicodeString()` deep-copy an existing `UNICODE_STRING`, replacing any existing destination buffer.
- `StartsWith()` performs a case-sensitive prefix test, with empty/null prefix treated as success.
- `ChangePrefix()` optionally requires an existing prefix, allocates a new string, copies a replacement prefix, then appends the original suffix.
- `IsMountPointDriveLetter()` recognizes mount points shaped like `\DosDevices\C:`, with or without a trailing null in `Length`.
- Search helpers scan for `WCHAR` values either backward from an offset or forward across a byte-length string.

## Integration Points
- Used by mount/device setup and FS control paths to classify drive-letter mount points, volume GUID mount points, and object-manager paths.
- `ChangePrefix()` is used by reparse/open-by-id style FS control handling to convert `\DosDevices\...` paths into `\??\...`.
- Search helpers are used by file info, create, event, and path handling code to locate stream separators, slashes, mount-point separators, and file-name offsets.
- Allocation helpers are used by initialization/device code for DCB names, symbolic links, mount points, UNC names, and mount manager names.

## Risks and Notes
- Prefix matching walks until a null terminator in the prefix buffer rather than strictly using `Prefix->Length`; this is safe for the defined constant strings but assumes valid null-terminated prefix buffers.
- `DokanDuplicateUnicodeString()` copies `MaximumLength`, not only `Length`, preserving trailing null/storage but requiring `Src->Buffer` and `Src->MaximumLength` to be valid.
- `DokanSearchWcharinUnicodeStringWithUlong()` compares `offsetPosition` to `MaximumLength` but then indexes `Buffer[offsetPosition]` as WCHAR units; callers need to pass offsets consistently.
- `ChangePrefix()` sets `MaximumLength` equal to the exact resulting byte length without reserving an extra terminator beyond the composed string.
