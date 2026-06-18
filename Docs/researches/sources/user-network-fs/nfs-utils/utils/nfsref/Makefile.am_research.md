## sources/user-network-fs/nfs-utils/utils/nfsref/Makefile.am

Purpose: Automake rules for the `nfsref` junction/referral management utility.

Important APIs/types/functions: Builds `nfsref` from `add.c`, `lookup.c`, `nfsref.c`, and `remove.c`, installs `nfsref.h` as a local header, and links against `support/nfs`, `support/junction`, libxml2, and libcap.

Control flow: Build-system only; automake emits targets for compile, link, install, and maintainer cleanup.

State and persistence: No runtime state. It declares the `nfsref.man` man page and generated `Makefile.in` cleanup.

Dependencies and integration: The junction library provides xattr/XML referral primitives; libcap likely supports privileged metadata operations.

Risks and test signals: Link failures or missing junction symbols are the main risk. Validate with build, install, and packaging checks that `nfsref.man` ships.
