# File Research: sources/virtualization/guestfs-tools/log/log.c

## Role

C implementation of `virt-log`, a read-only tool for displaying log files from an inspected virtual machine.

## Major Responsibilities

The program parses standard guestfs options, adds drives, launches libguestfs, mounts the single inspected root, and chooses a log extraction strategy based on guest type.

For Windows guests, it supports only Vista-or-newer event logs and delegates to `do_log_windows_evtx`. For Linux guests, it prefers a systemd journal under `/var/log/journal`; otherwise it tries `/var/log/syslog` and `/var/log/messages`.

## Linux Journal Output

`do_log_journal` opens the journal through guestfs APIs, iterates entries, extracts fields from xattrs, formats realtime timestamps as `"%b %d %H:%M:%S"`, prints identifier or command, PID, syslog priority name, and message. Priority defaults to info.

## Text And Windows Logs

Text logs are streamed directly with `guestfs_download` to `/dev/stdout`.

Windows EVTX support requires host `evtxdump.py`. The tool locates `System.evtx` case-sensitively, downloads it to a temporary file because python-evtx needs mmap-able input, then invokes `evtxdump.py` and reports process status failures.

## Research Notes

The implementation is intentionally read-only and inspector-driven. Its main risk surface is dependence on host external tooling for Windows EVTX parsing.
