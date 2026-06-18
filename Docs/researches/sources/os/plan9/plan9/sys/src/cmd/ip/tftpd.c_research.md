# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/tftpd.c

## Purpose
Implements a Plan 9 TFTP server. It serves RRQ/WRQ requests over UDP from a configured network mount point, defaults to service `69`, and defaults its root to `/lib/tftpd`.

## Main Behavior
The daemon parses `-d`, `-h`, `-r`, `-s`, and `-x`, becomes user `none`, builds a namespace, changes to the serving directory, announces `udp!*!service`, forks per connection, and handles one TFTP request per accepted data fd.

It supports RFC-style TFTP opcodes for read, write, data, ack, error, and option acknowledge. Reads use `sendfile`; writes use `recvfile`.

## Option Handling
Supports `timeout`, `blksize`, and `tsize` options. `options()` validates values, emits OACK packets, computes `tsize` from `dirstat`, and contains a network MTU workaround reducing large block sizes to `Bandtblksz`, except for a Cavium U-Boot block size.

## Path and Boot Handling
`-r` restricts paths by rejecting `#`, `../`, embedded `/../`, and absolute paths outside the serving root. `mapname()` expands one `%I`, `%C`, or `%E` using the remote IP and `/net/arp`. `sunkernel()` detects Sun-style hex IP boot requests and maps them through NDB `bootf`.

## Error and Retry Model
Read transfers wait for ACKs with alarms and retransmit up to `timeout` attempts. It tolerates Intel PXE EOF ACK quirks and block wraparound. Errors are sent with `nak()` and logged with `syslog`.

## Dependencies
Uses Plan 9 auth, Bio, IP, NDB, namespace, `/net`, and UDP conversation files. Filesystem relevance is serving and creating files inside a constrained namespace.
