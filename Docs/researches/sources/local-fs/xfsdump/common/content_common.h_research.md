# File Research: sources/local-fs/xfsdump/common/content_common.h

Purpose: declaration for shared content helper functionality.

Key declaration:
- `Media_prompt_change(drive_t *drivep)` asks the operator to confirm whether media was changed.

Interactions:
- Requires `drive_t` to be visible to the including translation unit.
- Implemented by `content_common.c`; used by content or drive workflows that need removable-media confirmation.

Risks/notes:
- Minimal header with no include guards beyond its own guard; callers must include required type definitions first.
