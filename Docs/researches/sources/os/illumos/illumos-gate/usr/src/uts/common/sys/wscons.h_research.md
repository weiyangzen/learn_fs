# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/wscons.h

`wscons.h` declares two small workstation-console vnode helpers. It includes `strredir.h`, `vnode.h`, and basic types.

`wcvnget()` obtains a `vnode_t *` for a console minor, and `wcvnrele()` releases that vnode. The signatures imply reference ownership is passed to and from callers through the returned vnode pointer.

The header is a narrow integration point between console minor devices, STREAMS redirection infrastructure, and vnode consumers.
