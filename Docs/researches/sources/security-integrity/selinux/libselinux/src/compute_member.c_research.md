# sources/security-integrity/selinux/libselinux/src/compute_member.c

Purpose: Computes member contexts through `selinuxfs/member`.

Important APIs/types/functions: `security_compute_member_raw()` queries the kernel using raw contexts and class. `security_compute_member()` translates public contexts before and after the raw query.

Control flow: the raw function validates `selinux_mnt`, opens `/member`, creates a page-sized request of `scon tcon class`, writes it, reads a raw context response, duplicates it, then closes and frees buffers.

State and persistence: stateless kernel query.

Dependencies and integration: used by `avc_compute_member()` to produce a `security_id_t` through the AVC SID table.

Risks and test signals: tests should cover missing mount, context conversion errors, class unmapping, buffer overflow, and response duplication failure.
