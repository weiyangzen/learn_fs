# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/stropts.h

`stropts.h` is the user/kernel STREAMS options and ioctl ABI header. It defines read/write mode bits, flush flags, signal/poll event bits, getmsg/putmsg flags, stream ioctl command numbers, and the user-visible structures passed to those ioctls.

Read options include normal, message-discard, and message-nondiscard modes (`RNORM`, `RMSGD`, `RMSGN`), plus protocol handling modes (`RPROTDAT`, `RPROTDIS`, `RPROTNORM`) and the private `RFLUSHPCPROT` behavior. Write options define zero-length message and SIGPIPE behavior. Error options control persistent versus nonpersistent read/write-side errors. Copy options advertise zero-copy safety and cache-copy preferences.

The event constants (`S_INPUT`, `S_HIPRI`, `S_OUTPUT`, `S_MSG`, `S_ERROR`, `S_HANGUP`, `S_RDNORM`, `S_RDBAND`, `S_WRBAND`, `S_BANDURG`) are used by `I_SETSIG`/`I_GETSIG` and stream poll/signal delivery. Message flags include classic `RS_HIPRI`, `MSG_HIPRI`, `MSG_ANY`, and `MSG_BAND`, plus kernel-private flags for internal `kstrgetmsg()`/`kstrputmsg()` behavior.

The ioctl namespace is rooted at `STR`. It defines module stack operations (`I_PUSH`, `I_POP`, `I_LOOK`, `I_FIND`, `I_LIST`), flushing and watermarks, `I_STR`, signal registration, mux link/unlink (`I_LINK`, `I_UNLINK`, `I_PLINK`, `I_PUNLINK`), descriptor passing (`I_SENDFD`, `I_RECVFD` with kernel/user numbering differences), message peeking/insertion, band operations, at-mark checks, error option accessors, private module insertion/removal, peer credential lookup, layered-driver plink support, and `_I_CMD`.

Data structures include `strioctl` and `strioctl32`, `strcmd_t` for private in-kernel command payloads, `strbuf` and `strbuf32`, `strpeek`/`strpeek32`, `strfdinsert`/`strfdinsert32`, receive-FD structures, `str_mlist`/`str_list`, private `strmodconf`, `bandinfo`, and extended signal set `strsigset`. The header carefully isolates XPG4.2 namespace variants and remaps `putmsg`/`putpmsg` to XPG4 entry points when needed.

Key relationship: `stream.h` consumes many of these flags in `stroptions`, getmsg/putmsg paths, and kernel helper APIs; `strsubr.h` carries the stream-head internal state that implements these user-visible options.
