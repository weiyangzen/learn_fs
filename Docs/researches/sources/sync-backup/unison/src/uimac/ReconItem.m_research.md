<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/unison/src/uimac/ReconItem.m -->
# sources/sync-backup/unison/src/uimac/ReconItem.m

Source read: complete file, 861 lines, 21654 bytes, sha256 `d485e4284dbadaac`.

Purpose: Implements reconciliation row models, display formatting, icon lookup, OCaml-backed leaf operations, and parent aggregation for the Mac UI outline table.

Important APIs/types/functions: Base `ReconItem` implements path/fullPath caching, change icons, file/direction/progress formatting, sort keys, action/ignore stubs, conflict/default checks, and diff hooks. `LeafReconItem` extracts fields from an OCaml recon item, calls OCaml functions for direction/actions/ignore/diff/details/progress, and caches details/progress. `ParentReconItem` manages children, nesting by path components, aggregate file counts/sizes/progress, conflict detection, action fanout, and single-child collapse.

Implementation inventory: discovered Objective-C/C callback methods include `dealloc, parent, setParent, willChange, children, selected, setSelected, path, setPath, fullPath, setFullPath, left, right, changeIconFor, leftIcon, rightIcon, computeFileSize, bytesTransferred, fileCount, fileSize, formatFileSize, fileSizeString, bytesTransferredString, percentTransferred, iconForExtension, fileIcon, dirString, direction` and more.

Control flow: Leaves are created with an OCaml value and index, then inserted under a root parent. The table asks rows for icons/text/progress and sort keys. User actions call `doAction:`/`doIgnore:`, which either call OCaml for a leaf or propagate through children for a parent. Progress and details are fetched lazily from OCaml and reset when needed; parent rows aggregate child states.

State and persistence behavior: Uses static dictionaries for change icons and file-extension icons. Instance caches include full path, direction image/sort string, file size, bytes transferred, details, and progress. Leaf state is backed by retained `OCamlValue` and list index; parent state is retained child arrays and aggregate file count.

Dependencies and integration points: Depends on AppKit image/workspace APIs, Carbon folder icon constants, the bridge, OCaml named functions for recon item field access/actions/diff, and table icon assets.

Risks: Manual memory management is complex. Static image caches can store nil if assets are missing. Bitwise `|` is used in a boolean check. Parent aggregate direction/conflict logic must stay consistent with OCaml action semantics. Lazy caches can become stale without `resetProgress` or direction invalidation.

Test signals: Unit-style construction of leaf/parent trees, action propagation, ignore removal, conflict selection, sorting, collapse behavior, diff enablement, file-size formatting, and progress aggregation. GUI tests should verify icons and direction changes after user commands.
<!-- END_FILE_RESEARCH: sources/sync-backup/unison/src/uimac/ReconItem.m -->
