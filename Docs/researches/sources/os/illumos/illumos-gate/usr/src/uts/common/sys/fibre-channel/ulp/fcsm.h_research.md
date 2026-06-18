# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/ulp/fcsm.h

Defines the SAN Management ULP private state and ioctl interface. Kernel-only definitions include message destinations, debug levels, open flags, ELS/management-server timeouts, retry constants, job structure `fcsm_job_t`, per-port state `fcsm_t`, and command wrapper `fcsm_cmd_t`.

`fcsm_t` tracks per-port SAN management state: mutex, global list linkage, S_ID, instance, port state/topology, flags, pending command and callback counts, ULP port info, job queue, retry queue, timers, job condition variable, discovered device map, per-port job thread, command cache, management-server login parameters, and CPR state.

The public ioctl portion defines `fc_ct_aiu_t`, `FCSMIO_CMD`, subcommands for CT passthrough and adapter lookup, maximum CT payload size, and many management-server/fabric-configuration command codes. Kernel prototypes cover driver entry points, ULP callbacks, attach/detach/resume, job and command queues, management-server login, CT passthrough, retry handling, and formatting helpers.
