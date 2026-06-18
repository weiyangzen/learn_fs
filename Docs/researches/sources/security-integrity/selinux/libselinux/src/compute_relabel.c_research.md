# sources/security-integrity/selinux/libselinux/src/compute_relabel.c

Purpose: Computes relabel contexts through `selinuxfs/relabel`.

Important APIs/types/functions: `security_compute_relabel_raw()` is the raw kernel-query API; `security_compute_relabel()` is the translated public wrapper.

Control flow: raw relabel computation opens `/relabel`, formats `scon tcon class`, writes the request, reads the new raw context, and duplicates it. The public wrapper translates source/target contexts to raw and converts output back to translated form.

State and persistence: no persistent state is changed by this query.

Dependencies and integration: depends on `selinux_mnt`, `selinux_page_size`, `unmap_class()`, and raw/trans context conversion helpers.

Risks and test signals: same page-sized request constraints as other compute APIs. Tests should cover invalid contexts, unsupported class, long request, read/write failure, and output conversion failure.
