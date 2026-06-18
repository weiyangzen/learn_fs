# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/NameChanger/nccreate.c

This file implements pre-create namespace redirection. Its job is to hide the real mapping and redirect opens under the user mapping to the real backing location.

`NcPreCreate` early-passes operations that are name-agnostic or unsupported for virtualization:
- Paging file opens.
- Volume opens.
- Opens by file ID.

It obtains the opened name with `FLT_FILE_NAME_OPENED | FLT_FILE_NAME_QUERY_DEFAULT | FLT_FILE_NAME_DO_NOT_CACHE`, parses it, retrieves the instance context, and compares the opened path against both real and user mappings.

Real mapping behavior:
- Exact open of the real mapping is completed without reaching the filesystem.
- `FILE_OPEN` and `FILE_OVERWRITE` get `STATUS_OBJECT_NAME_NOT_FOUND`.
- Create-like dispositions get `STATUS_ACCESS_DENIED`.
- Descendants under the real mapping get `STATUS_OBJECT_PATH_NOT_FOUND`.
This preserves the illusion that the real location is not visible.

Delete protection:
- If `FILE_DELETE_ON_CLOSE` is used on an ancestor of either mapping, the open is denied. This prevents users from deleting/renaming mapping ancestors and invalidating cached long/short-name assumptions.

User mapping behavior:
- If the opened path is inside the user mapping, the remainder under the user mapping is calculated.
- For `SL_OPEN_TARGET_DIRECTORY`, the code temporarily clears the flag and requeries the full opened name including the final component, then restores the flag.
- It constructs the corresponding real path with `NcConstructPath`.
- It replaces the file object name through `NcReplaceFileObjectName`.
- It clears `RelatedFileObject` because the new name is already full.
- It lets the create continue to the filesystem with the munged real name.

Important dependencies:
- `NcComparePath` determines mapping overlap.
- `NcConstructPath` builds the redirected real path.
- `NcReplaceFileObjectName` is supplied by `nccompat.c`.
- Instance mapping state is built during `NcInstanceSetup`.

Notable behavior:
- The opened name is intentionally queried without going through the filter’s own name provider to avoid converting real names back to user names and poisoning lower name caches.
- No post-create callback is required; the visible name illusion is maintained by name-provider and information-query paths elsewhere.
