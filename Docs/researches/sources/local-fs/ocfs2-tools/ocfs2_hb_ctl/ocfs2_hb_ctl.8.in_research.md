# File Research: sources/local-fs/ocfs2-tools/ocfs2_hb_ctl/ocfs2_hb_ctl.8.in

This manpage documents `ocfs2_hb_ctl`, a helper for starting/stopping local O2CB heartbeat on an OCFS2 device by device path or UUID. It explicitly warns users not to run it directly because it is invoked by mount and other tools.

Documented actions include start, stop, reference count display, and heartbeat thread I/O priority adjustment through `ionice`. It states the tool only operates in local heartbeat mode and silently fails in global heartbeat mode.
