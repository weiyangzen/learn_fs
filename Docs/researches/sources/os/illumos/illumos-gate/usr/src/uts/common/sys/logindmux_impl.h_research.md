# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/logindmux_impl.h

## Role

Private implementation header for logindmux peer unlink coordination and per-instance STREAMS state.

## Structure

Includes types and STREAMS headers, defines `unlinkinfo_t` shared between peers, `struct tmx` per open instance, module ID, timer wait constants, peer linkage states, protocol message values, and `LOGDMUX_PROTO_MBLK()` to identify unlink protocol messages.

## Dependencies And Consumers

Depends on STREAMS `queue_t`, `mblk_t`, `struct iocblk`, `DB_TYPE`, `M_CTL`, `M_IOCTL`, `I_UNLINK`, mutexes, bufcall IDs, and timeout IDs. Consumed by logindmux module implementation.

## Important Details

`unlinkinfo_t` serializes I_UNLINK handling so only one peer actively processes unlink at a time. `LOGDMUX_PROTO_MBLK()` assumes the message has a continuation block and checks for an embedded `I_UNLINK` ioctl.

## Research Notes

Read completely: 109 lines, 3258 bytes.
