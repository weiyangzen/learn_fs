<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/unison/src/uimac/ProgressCell.m -->
# sources/sync-backup/unison/src/uimac/ProgressCell.m

Source read: complete file, 199 lines, 7263 bytes, sha256 `0f5fb3812aaf592f`.

Purpose: Implements a custom progress/status cell using bundled Transmission-derived progress bar image slices.

Important APIs/types/functions: `+initialize` loads static images, `drawBarImage:width:point:`, `drawBar:point:`, `drawWithFrame:inView:`, setter methods, `copyWithZone:`, and `dealloc` are the key methods.

Implementation inventory: discovered Objective-C/C callback methods include `initialize, init, dealloc, setStatusString, setIcon, setIsActive, drawBarImage, drawBar, drawWithFrame, copyWithZone`.

Control flow: Class initialization loads progress and error assets. Drawing computes progress from `[self objectValue]` over `_minVal.._maxVal`, composites left cap, filled bar, remaining bar, and right cap, then draws optional icon and centered status text with highlight-aware color.

State and persistence behavior: Static image cache is process-wide. Each cell instance tracks active state, icon, and status string. The object value supplies numeric progress.

Dependencies and integration points: Depends on progress image assets under `progressicons`, `Error.tiff`, AppKit image compositing, and `MyController` table display code.

Risks: `setStatusString:` and `setIcon:` retain new values without releasing old values, leaking on repeated updates. `_isError` and `_useFullView` exist but are not publicly configured in this file. Deprecated compositing APIs may require modernization.

Test signals: Use the table during a real sync and inspect progress rendering; run leak checks while progress updates repeatedly; verify all named image assets are present in the bundle.
<!-- END_FILE_RESEARCH: sources/sync-backup/unison/src/uimac/ProgressCell.m -->
