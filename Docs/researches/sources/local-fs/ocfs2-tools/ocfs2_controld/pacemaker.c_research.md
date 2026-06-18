# File Research: sources/local-fs/ocfs2-tools/ocfs2_controld/pacemaker.c

`pacemaker.c` is the Pacemaker stack adapter for `ocfs2_controld`. It initializes CRM/AIS cluster communication, records local node name/id, subscribes to membership notifications, adds the AIS fd to the daemon poll loop, and dispatches AIS messages when readable.

It implements the same stack interface as `cman.c`: cluster name validation, cluster name lookup, node id to name via CRM peers, node kill via `crm_terminate_member_no_mainloop()`, setup, and teardown. The reported cluster name is the fixed string `pacemaker`.

Risks include old Pacemaker/AIS API dependencies, `nodeid2name()` assuming `crm_get_peer()` succeeds, and dynamically adding a stonith fd during node kill if Pacemaker returns one.
