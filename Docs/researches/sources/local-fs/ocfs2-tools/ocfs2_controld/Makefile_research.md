# File Research: sources/local-fs/ocfs2-tools/ocfs2_controld/Makefile

This makefile builds stack-specific `ocfs2_controld` daemons: `ocfs2_controld.cman` when CMAN support is enabled and `ocfs2_controld.pcmk` when Pacemaker support is enabled. Shared daemon sources are `main.c`, `cpg.c`, `mount.c`, `ckpt.c`, and `dlmcontrol.c`; stack adapters are `cman.c` or `pacemaker.c`.

It links against `libo2cb`, OpenAIS checkpoint, Corosync/OpenAIS CPG, dlmcontrol, and stack-specific CMAN or Pacemaker/CRM libraries. It also builds an uninstalled `test_client` with `libocfs2` and `libo2cb`.

Build defines include flat include compatibility macros, optional `HAVE_COROSYNC`, and `VERSION`. This is the integration point for the controld daemon’s cluster-stack variants.
