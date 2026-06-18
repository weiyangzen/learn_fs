# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/nlm/sm_inter.h

Rpcgen-generated header for the Network Status Monitor protocol used by lockd. It defines SM program/version constants, procedure numbers, C structs, enum results, client/server prototypes, freeresult prototype, and XDR declarations.

Defined structures include monitored names, callback identity (`my_id`), monitor ids, monitor requests with 16-byte private cookies, state-change records, simple state replies, monitor result replies, and status notifications. Procedures include `SM_STAT`, `SM_MON`, `SM_UNMON`, `SM_UNMON_ALL`, `SM_SIMU_CRASH`, and `SM_NOTIFY`.

Within this group, `nlm_prot_impl.c` uses these definitions to register/unregister remote hosts with the local NSM and to clear monitor state at lockd startup.
