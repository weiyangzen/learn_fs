# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/impl/fp.h

Defines private declarations for the fp port driver implementation. It provides trace levels/destinations, `FP_DTRACE`/`FP_TRACE` wrappers, packet-error testing, discovery/timeouts/retry constants, task states, command flags, DMA flags, open flags, and message-control constants.

Main structures are `fp_soft_attach_t`, `fp_cmd_t`, and `fp_unsol_spec_t`. `fp_cmd_t` wraps an `fc_packet_t` for fp internal ELS/name-service operations, with DMA state, retry timing, job association, ULP packet linkage, and transport function pointer.

Most of the file is a prototype map for fp implementation paths: attach/detach/power/open/close/ioctl, packet allocation/freeing, job handling, startup/shutdown, loop/fabric/point-to-point online handling, FLOGI/PLOGI/LOGO/ADISC/RLS/RNID, state-change callbacks, name-service registration/query/GAN handling, FCIO command copyin/copyout, unsolicited ELS handling, RSCN validation, ULP attach/notification, target logout/login, and port capability retrieval.
