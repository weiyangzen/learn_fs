# File Research: sources/local-fs/ocfs2-tools/ocfs2console/ocfs2interface/fswidgets.py

Reusable PyGTK widgets for OCFS2 format/tune parameters.

Key classes:
- `BaseCombo`
  - Uses `gtk.ComboBox` for PyGTK >= 2.4.
  - Falls back to `gtk.Combo` on older PyGTK.
  - Provides `get_choice()` and `set_choices()`.
- `ValueCombo`
  - Builds power-of-two size choices from min to max plus `Auto`.
  - Converts chosen text into command-line args.
- `NumSlots`
  - Spin button from 1 to `ocfs2.MAX_SLOTS`, default 4.
  - Produces `('-N', value)`.
- `VolumeLabel`
  - Entry capped at `ocfs2.MAX_VOL_LABEL_LEN`.
  - Produces `('-L', label)`.
- `ClusterSize`
  - Size combo from `ocfs2.MIN_CLUSTERSIZE` to `ocfs2.MAX_CLUSTERSIZE`.
  - Produces `-C`.
- `BlockSize`
  - Size combo from `ocfs2.MIN_BLOCKSIZE` to `ocfs2.MAX_BLOCKSIZE`.
  - Produces `-b`.

Dependencies:
- `ocfs2` constants from C extension
- `guiutil.format_bytes`

Notable details:
- Designed for command assembly in `format.py` and likely tuning modules.
- Old PyGTK compatibility is explicit throughout.
