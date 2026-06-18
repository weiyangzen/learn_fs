# File Research: sources/local-fs/xfsprogs/db/convert.c

Purpose: implements `convert` and `rtconvert`, commands that translate among XFS address forms.

Key behavior:
- Defines conversion types for AG block, AG inode, AG number, byte offset in basic block/fsblock/inode, filesystem byte, disk address, fsblock, inode, inode index, inode offset, realtime block, realtime extent, realtime bitmap block/word, realtime summary block/log/info, realtime group block, and realtime group number.
- Each conversion type has accepted aliases, for example `fsblock/fsb/fsbno`, `daddr/bb`, `ino/inode`, `rtblock/rtb/rtbno`, `rgnumber/rgno`.
- `ctydescs` defines legal combinations for regular filesystem address conversions.
- `ctydescs_rt` defines legal combinations for realtime address conversions.
- `convert_f` parses one or more `type value` inputs plus a final output type, rejects conflicting or identical result types, uses `cur_agno` as an implicit AG number when possible, converts inputs to a byte offset, then derives the requested regular output type.
- `rtconvert_f` performs equivalent realtime-device conversions, including realtime groups, bitmap words/blocks, and realtime summary block/info computations.
- `rsumlog` and `rsuminfo` are special context inputs required for realtime summary reverse mappings.
- `convert_init` registers both commands.

Interactions:
- Uses mount geometry from global `mp`, including block size, inode size, AG size, realtime extent size, realtime bitmap geometry, and realtime group geometry.
- Uses libxfs helpers such as `xfs_daddr_to_rtb`, `xfs_rtb_to_daddr`, `xfs_rtx_to_rbmblock`, `xfs_rtsumoffs`, and realtime group metadata.

Risks/notes:
- The command computes numerically; it does not validate that the resulting address points to live metadata.
- Realtime summary conversions require `rsumlog` and sometimes `rsuminfo` to appear in the input set before converting summary block/info addresses.
- Some realtime group conversions return zero when realtime groups are not enabled.
