# sources/user-network-fs/libsmb2/examples/smb2-ls-epoll.c

Purpose: This Linux-only example shows how to integrate libsmb2's async fd callbacks with `epoll` while listing a directory.

Important APIs and types: It uses Linux `epoll_create1`, `epoll_ctl`, `epoll_wait`, libsmb2 fd/event callbacks, `smb2_set_opaque`, `smb2_get_opaque`, async connect/opendir/disconnect APIs, and directory entry iteration.

Control flow: On Linux, the program creates an SMB2 context, stores an `e_data` structure as opaque data, creates an epoll fd, registers fd/event callbacks that add/delete/modify epoll interest, starts async share connect, then waits in `epoll_wait` and calls `smb2_service` for returned events. Non-Linux builds compile a stub that reports epoll is required.

State and persistence behavior: Runtime state is `e_data`, epoll interest state, `is_finished`, URL/context, and directory handles. It persists nothing.

Dependencies and integration points: It exercises the same listing path as `smb2-ls-async.c` but with edge integration expected by high-performance Linux event loops.

Risks: `ed` is a stack object referenced through the SMB2 context; this is safe only while `main` is active. The callback exits on epoll errors. The initial event registration before connect may have fd `-1` and is guarded only by a nonnegative check.

Test signals: On Linux, directory listing should complete while epoll add/mod/del calls succeed. On non-Linux, the stub should compile and print the unsupported message.
