# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/ugen/ugend.h

Internal USB generic driver support skeleton header. It defines a small `ugen_skel_state_t` containing device info, instance, and `usb_ugen_hdl_t`.

Constants cover soft-state instance count and minor-number packing: 9 bits reserved for ugen minor data, with remaining bits mapped back to instance via `UGEN_MINOR_TO_INSTANCE()`.

The state is marked readable without lock by Warlock annotations.
