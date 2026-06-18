## sources/distributed-fs/xrootd/src/XrdNet/XrdNetCmsNotify.cc

Purpose: Sends cache-manager notification datagrams for file availability changes.

Important APIs and functions: Constructor builds destination path and message sender; destructor releases them. `Have`, `Gone`, and private `Send` format and transmit CMS commands.

Control flow: Construction derives an instance-specific `.olb` path and appends `olbd.notes` for server mode or `olbd.seton` otherwise, then creates an `XrdNetMsg`. `Have` emits `have  ` or `newfn `; `Gone` emits `gone  ` or `rmdid `; both append the path and newline. `Send` optionally serializes calls with a static mutex and 10 ms wait before calling `XrdNetMsg::Send`.

State and persistence: Per-object state is logger, `XrdNetMsg`, destination path, and pacing flag. Notifications are transient UDP/Unix socket messages; no persistent state is stored here.

Dependencies and integration points: Uses `XrdNetMsg`, `XrdOucUtils::InstName`, `XrdOucUtils::genPath`, `XrdSysTimer`, and `MAXPATHLEN`. Integrates file-server events with olbd/cms notification sockets.

Risks: Constructor uses fixed `char buff[1024]` with `strcpy`/`strcat` after `genPath`; long admin paths can overflow despite path commands later checking `MAXPATHLEN`. Static pacing mutex serializes all instances. Return mapping treats positive send timeouts as `-ETIMEDOUT`.

Test signals: Build destinations for service and non-service modes, with and without instance names; send `Have`/`Gone` for PFN and logical names; test long paths, send timeouts, noPace mode, and missing notification socket.
