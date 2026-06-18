# File Research: sources/os/plan9/9front/sys/src/lib9p/post.c

## Read Status
Complete: 48 lines read.

## Purpose
Posts a 9P server through a pipe, optionally advertising the read fd in `/srv`.

## Main Responsibilities
- Create a pipe for client/server communication.
- Optionally create `/srv/<name>` and write the client-side fd number.
- Configure `Srv.infd` and `Srv.outfd` to the server-side pipe fd.
- Start the server in a separate execution context.
- Return the client-side fd to the caller.

## Important Functions
- `postsrv`: main posting helper.
- `postproc`: child/server entry that rendezvous-closes the client fd and runs `srv`.

## Dependencies and Interactions
- Uses `rendezvous` to coordinate fd ownership.
- Uses `srvforker` unless `Srv.forker` is already set.
- Called by `postmountsrv`, `postsharesrv`, and thread wrappers.
