## sources/user-network-fs/nfs-utils/utils/statd/Makefile.am

Purpose: Automake rules for `rpc.statd`, `sm-notify`, generated RPC simulation files, scripts, and man pages.

Important APIs/types/functions: Builds `statd` from callback, monitor, notification-list, RPC call, daemon, service-loop, and helper sources; builds `sm-notify` from `sm-notify.c`; installs `start-statd`; generates RPC files from `sim_sm_inter.x` when configured; renames installed `statd` with `rpc.`/kernel prefixes.

Control flow: Build and install hooks transform daemon names and create man-page symlinks.

State and persistence: No runtime state in this file, but it wires programs that use NSM state directories and pid files.

Dependencies and integration: Links `support/nsm`, `support/nfs`, `support/misc`, libwrap, libnsl, libcap, and libtirpc.

Risks and test signals: Install hooks are custom and can diverge from automake expectations. Validate generated RPC file creation, prefixed binary install/uninstall, man links, and clean targets.
