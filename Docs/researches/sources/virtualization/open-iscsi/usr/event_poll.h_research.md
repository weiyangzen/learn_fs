# File Research: sources/virtualization/open-iscsi/usr/event_poll.h

Declares process reaping, shutdown callback, reload tracking, event loop, and event loop exit APIs. It forward-declares `iscsi_ipc` and `queue_task`.

Minor typo: the reload tracking prototype names its PID parameter `realod_proc_pid`, while the implementation uses `reload_proc_pid`.
