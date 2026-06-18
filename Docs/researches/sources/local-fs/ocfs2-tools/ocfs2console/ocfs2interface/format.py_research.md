# File Research: sources/local-fs/ocfs2-tools/ocfs2console/ocfs2interface/format.py

GUI workflow for formatting an unmounted partition as OCFS2.

Key classes:
- `Device(BaseCombo)`
  - Lists available unmounted partitions.
  - Extracts device name from combo text.
- `FormatVolumeLabel(VolumeLabel)`
  - Defaults label text to `oracle`.

Key function:
- `format_partition(parent, device)`
  - Calls `partition_list(..., unmounted=True)`.
  - Shows error if no unmounted partitions exist.
  - Presents dialog fields:
    - available device
    - volume label
    - cluster size
    - number of node slots
    - block size
  - Confirms destructive format action.
  - Builds `mkfs.ocfs2 -x` command plus widget-derived args.
  - Runs via `Process`.
  - Shows error dialog on failure.

Dependencies:
- `plist.partition_list`
- `fswidgets`
- `process.Process`
- `guiutil.Dialog`, `error_box`

Notable details:
- Uses argument list form for `Process`, reducing shell parsing risk here.
- The base command includes `-x`, likely selecting expert/noninteractive behavior for mkfs.
