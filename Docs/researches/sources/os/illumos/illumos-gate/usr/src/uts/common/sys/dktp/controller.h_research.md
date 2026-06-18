# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dktp/controller.h

## Scope

Complete file read, 105 lines. This header defines the DKTP controller object abstraction and controller-operation dispatch macros.

## Public Surface

It exports:

- `struct ctl_ext`: controller type cookie, controller and target devinfo pointers, target number, and block size.
- `struct ctl_obj`: object data pointer, ops table, extension pointer, and embedded extension storage.
- `struct ctl_objops`: callbacks for packet allocation/free, DMA memory setup/free, I/O setup, transport, reset, abort, get/set capability, ioctl, and reserved slots.
- Access macros such as `CTL_DIP_CTL`, `CTL_DIP_DEV`, `CTL_GET_TYPE`, `CTL_GET_TARG`, and `CTL_GET_BLKSZ`.
- Dispatch macros `CTL_PKTALLOC`, `CTL_PKTFREE`, `CTL_MEMSETUP`, `CTL_MEMFREE`, `CTL_IOSETUP`, `CTL_TRANSPORT`, `CTL_ABORT`, `CTL_RESET`, and `CTL_IOCTL`.
- Transport results `CTL_SEND_SUCCESS`, `CTL_SEND_FAILURE`, and `CTL_SEND_BUSY`.

## Behavior And Integration

The target disk layer uses this object interface to allocate command packets, prepare buffers, send commands to hardware/SCSI transports, and issue reset/abort/ioctl operations without binding to a concrete controller.

## Dependencies And Invariants

The object pointer must be a valid `struct ctl_obj *`, with `c_ext` and `c_ops` initialized. `struct cmpkt`, `struct buf`, `dev_info_t`, `opaque_t`, and callback types must come from included context.

## Risks

`CTL_GET_LKARG` references `c_lkarg`, but `struct ctl_ext` in this header does not define that field. Code using that macro must rely on a different historical layout or will fail to compile. All dispatch macros are unchecked direct function-pointer calls.
