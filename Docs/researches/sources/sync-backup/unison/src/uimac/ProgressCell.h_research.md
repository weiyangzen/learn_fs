<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/unison/src/uimac/ProgressCell.h -->
# sources/sync-backup/unison/src/uimac/ProgressCell.h

Source read: complete file, 15 lines, 411 bytes, sha256 `cab15ab31bba726d`.

Purpose: Declares a custom cell for displaying per-item synchronization progress, status text, and optional icons in the reconciliation outline.

Important APIs/types/functions: Exports setters for status string, icon, and active state. Internal fields track min/max, active/full/error flags, icon, and status text.

Implementation inventory: discovered Objective-C/C callback methods include `setStatusString, setIcon, setIsActive`.

Control flow: The table delegate configures the cell per row from `ReconItem` progress values before AppKit calls drawing.

State and persistence behavior: State is retained icon/status text and draw flags per cell copy.

Dependencies and integration points: Depends on AppKit `NSCell` and image assets loaded by the implementation.

Risks: The header exposes only setters, so object value and hidden flags must be coordinated by table code and implementation defaults.

Test signals: Render inactive, active, complete, empty, text-only, and icon states in selected and unselected rows.
<!-- END_FILE_RESEARCH: sources/sync-backup/unison/src/uimac/ProgressCell.h -->
