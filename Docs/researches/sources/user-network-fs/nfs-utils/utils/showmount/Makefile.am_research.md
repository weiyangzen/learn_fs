## sources/user-network-fs/nfs-utils/utils/showmount/Makefile.am

Purpose: Automake rules for building `showmount`.

Important APIs/types/functions: Builds `showmount.c`, links export/nfs/misc support libraries and libtirpc, and adds the export support include path.

Control flow: Build-only.

State and persistence: No runtime state; distributes `showmount.man`.

Dependencies and integration: Depends on RPC/TI-RPC and nfs-utils support libraries used by `showmount.c`.

Risks and test signals: Validate with builds against libtirpc and install/distribution checks for binary plus man page.
