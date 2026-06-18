# File Research: sources/teaching/minix/minix/fs/ptyfs/Makefile

This makefile builds the PTYFS service as program `ptyfs` from `ptyfs.c` and `node.c`. It links against `libfsdriver` and includes `<minix.service.mk>` for service build integration.

Within this grouped scope, only the node-management companion files are included for source research; the makefile shows that `node.c` is part of the full PTYFS service.
