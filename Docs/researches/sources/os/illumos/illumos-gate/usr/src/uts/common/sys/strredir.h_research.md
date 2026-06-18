# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/strredir.h

`strredir.h` declares the STREAMS redirection driver/module interface. It assigns `STRREDIR_MODID` and uses that module ID to form two ioctls: `SRIOCSREDIR` to set a redirection target and `SRIOCISREDIR` to query whether a stream is a redirection target.

The comments note that module ID uniqueness is not centrally administered, which matters because ioctl cookie values are derived from the module ID. Kernel-only content names the close-detection module (`redirmod`) and declares `srpop(vnode_t *, boolean_t)`, used to pop/clean redirection module state from a stream vnode.
