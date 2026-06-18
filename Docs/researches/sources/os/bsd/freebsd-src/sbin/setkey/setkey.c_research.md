# File Research: sources/os/bsd/freebsd-src/sbin/setkey/setkey.c

## Summary
Main command-line driver for `setkey`. It opens PF_KEY, loads the IPsec module if needed, dispatches script/dump/flush/promiscuous modes, sends PF_KEY messages, receives replies, and formats SAD/SPD output.

## Main Responsibilities
- Parses command modes: script from stdin/file/string, SAD/SPD dump, SAD/SPD flush, and PF_KEY promiscuous monitor.
- Supports flags for all entries, looping dump, hex dump, policy mode, global/interface policy scope, verbose debug output, and receive-timeout control.
- Loads `ipsec` kernel module when absent.
- Registers supported algorithms before parsing scripts.
- Sends PF_KEY messages and post-processes replies.
- Dumps SAD entries, SPD entries, and short looped SAD summaries.
- Filters dead SAs from normal dumps unless `-a` is used.
- Prints timestamps for promiscuous PF_KEY monitoring.

## Key Elements
- `main()`: option parsing and mode dispatch.
- `sendkeyshort()`: minimal PF_KEY command sender for dump/flush.
- `sendkeymsg()`: common send/receive loop with optional verbose and hex output.
- `postproc()`: formats errors and dump/get replies.
- `promisc()`: subscribes to PF_KEY promiscuous messages.
- `shortdump()` / `shortdump_hdr()`: compact SAD monitoring output.
- `gmt2local()` / `printdate()`: timestamp support.

## Dependencies And Integration
Uses `libpfkey`, netipsec headers, `parse()` from `token.l`/`parse.y`, kernel module loading APIs, and PF_KEY raw sockets.
