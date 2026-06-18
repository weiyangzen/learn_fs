# sources/user-network-fs/libsmb2/examples/smb2-ls-async.c

Purpose: This example asynchronously lists a remote SMB directory.

Important APIs and types: It uses `smb2_connect_share_async`, `smb2_opendir_async`, `smb2_readdir`, `smb2_closedir`, `smb2_disconnect_share_async`, fd/event callbacks, `smb2_service`, `smb2dir`, `smb2dirent`, and stat fields such as `smb2_type`, `smb2_size`, and `smb2_mtime`.

Control flow: The connect callback starts async directory open. The open callback iterates all cached directory entries synchronously through `smb2_readdir`, prints type/size/time, closes the directory, and disconnects asynchronously. The main loop polls callback-maintained fd/events until disconnect marks completion.

State and persistence behavior: Runtime state is global `is_finished`, current fd/events, the parsed URL, and the directory handle. It only prints to stdout.

Dependencies and integration points: It demonstrates libsmb2 async connection and fd event callback integration with `poll`. It includes Amiga/AROS poll compatibility.

Risks: Output uses `asctime(localtime())`, which is not thread-safe and embeds a newline. Error paths exit immediately. The fd callback model assumes a single active fd.

Test signals: Directory listings should include correct names, file/directory/link type labels, sizes, and mtimes. Async fd event changes should drive the program without busy looping.
