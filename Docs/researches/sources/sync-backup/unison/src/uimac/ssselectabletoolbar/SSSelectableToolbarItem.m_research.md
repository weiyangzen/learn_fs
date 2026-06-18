<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/unison/src/uimac/ssselectabletoolbar/SSSelectableToolbarItem.m -->
# sources/sync-backup/unison/src/uimac/ssselectabletoolbar/SSSelectableToolbarItem.m

Source read: complete file, 22 lines, 355 bytes, sha256 `63f46bdd6b7f49ca`.

Purpose: Implements property synthesis and cleanup for selectable toolbar items.

Important APIs/types/functions: Synthesizes `linkedView` and releases it in `dealloc`.

Implementation inventory: discovered Objective-C/C callback methods include `dealloc`.

Control flow: There is no runtime behavior beyond storage; the owning toolbar performs selection/content switching.

State and persistence behavior: One retained view pointer per toolbar item.

Dependencies and integration points: Depends on `SSSelectableToolbarItem.h` and AppKit `NSToolbarItem` lifecycle.

Risks: Manual reference counting requires the release in `dealloc`; ownership must align with nib loading semantics.

Test signals: Run leak/static analyzer checks and verify toolbar items retain linked views through window switches.
<!-- END_FILE_RESEARCH: sources/sync-backup/unison/src/uimac/ssselectabletoolbar/SSSelectableToolbarItem.m -->
