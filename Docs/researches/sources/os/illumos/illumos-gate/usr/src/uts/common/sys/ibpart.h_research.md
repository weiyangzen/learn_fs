# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ibpart.h

This header defines ioctl ABI structures and commands for InfiniBand partition management.

Key definitions:
- Ioctl commands: `IBD_CREATE_IBPART`, `IBD_DELETE_IBPART`, `IBD_INFO_IBPART`.
- Info subcommands: `IBD_INFO_CMD_IBPART`, `IBD_INFO_CMD_IBPORT`, `IBD_INFO_CMD_PKEYTBLSZ`.
- Error enum `ibd_part_err_t` covers invalid port instance, down port, missing/invalid P_Key, partition exists, no hardware resource, and invalid P_Key table size.

Structures:
- `ibd_ioctl_t` carries common ioctl fields: info command, datalink ID, port instance/number, HCA/port GUIDs, status, and alignment padding.
- `ibpart_ioctl_t` extends common data with partition datalink ID, force-create flag, P_Key, and padding.
- `ibd_create_ioctl_t` and `ibd_delete_ioctl_t` alias `ibpart_ioctl_t`.
- `ibport_ioctl_t` reports P_Key table size and pointer to P_Key array.
- Under `_SYSCALL32`, `ibport_ioctl32_t` provides a 32-bit pointer-compatible form.

ABI notes:
- Comments explicitly warn that structure alignment must remain correct for 32-bit and 64-bit ioctl operation.
- Depends on stable datalink and InfiniBand type sizes.

Dependencies:
- Includes `sys/types.h`, `sys/ib/ib_types.h`, and `sys/dld_ioc.h`.

Relevance:
- Network/storage substrate support: InfiniBand partitioning can affect RDMA-capable storage connectivity.
