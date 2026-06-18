# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/factotum/fs.c

Defines factotum’s 9P file server and process entry point. `main` parses flags, optionally protects itself with `private` and `noswap`, initializes protocol table entries, loads nvram/secstore keys, and posts/mounts the service.

The exported tree is `/factotum` with files `confirm`, `needkey`, `ctl`, `rpc`, `proto`, and `log`. `confirm`, `needkey`, and `log` are exclusive where appropriate; `rpc` is world-readable/writable for authentication exchanges; `ctl` accepts key-management writes and lists keys on read.

Open allocates an `Fsstate` per fid, read dispatches to RPC/confirm/needkey/log/list handlers, write dispatches to `rpcwrite`, `needkeywrite`, `confirmwrite`, or `ctlwrite`, and destroy closes active protocol state.

Important behavior: server mode `-S` disables prompting and loads nvram only; `-g` prompts for a key and sends it to an existing factotum; secstore fetching can be driven by nvram config password. This file is the central integration point for all factotum protocol modules.
