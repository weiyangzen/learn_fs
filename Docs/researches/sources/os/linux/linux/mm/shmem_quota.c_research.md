# File Research: sources/os/linux/linux/mm/shmem_quota.c

Implements the in-memory quota format used by tmpfs when `CONFIG_TMPFS_QUOTA` is enabled. Since tmpfs has no persistent quota file, this format stores quota limits and tracked ids in kernel memory while delegating active dquot accounting to the generic quota layer.

Key responsibilities:
- Defines quota grace periods and a per-id `struct quota_id` containing user/group id plus block and inode hard/soft limits.
- Provides `quota_format_ops` for the fake shmem quota format: quota-file checking, quota info setup, quota info write no-op, and full teardown.
- Allocates one red-black tree root per quota type in `mem_dqinfo->dqi_priv`.
- Implements `get_next_id` by walking the sorted id tree under the quota I/O semaphore.
- Implements dquot acquire by finding or creating a `quota_id` entry, applying tmpfs global default hard limits for new ids, loading limits into the dquot, and marking it active.
- Implements dquot release by either removing empty/fake ids from the tree or saving current dquot limits back into the tree.
- Exports `shmem_quota_format` and `shmem_quota_operations` for `shmem.c` to register and attach to tmpfs superblocks.

Important behavior:
- There is deliberately no on-disk quota file; check/write operations are successful no-ops.
- `dqi_max_spc_limit`, `dqi_max_ino_limit`, block grace, and inode grace are initialized when quota tracking is enabled.
- New user/group ids inherit default hard limits from `struct shmem_sb_info::qlimits`; soft limits default to zero until explicitly changed.
- Dquots with no useful state are marked fake and can be removed from the in-memory tree on release.
- The tree is protected by `dqio_sem`; individual dquot state is protected by `dq_lock` and `dq_dqb_lock`.

Dependencies:
- Uses generic Linux quota/dquot infrastructure, `mem_dqinfo`, rbtrees, tmpfs `struct shmem_sb_info`, and id conversion through `init_user_ns`.

Notable risks:
- All quota state is volatile. If a dquot were shrinkable like persistent quota formats, limits would be lost, so this code intentionally keeps state in the red-black tree until quota teardown or an empty release.
- `shmem_is_empty_dquot()` assumes only supported quota types reach it; additional quota types would need explicit handling.
- Correct limit persistence depends on release paths storing modified limits before clearing `DQ_ACTIVE_B`.
