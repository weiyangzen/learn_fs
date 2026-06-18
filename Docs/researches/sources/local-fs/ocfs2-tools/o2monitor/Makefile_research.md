# File Research: sources/local-fs/ocfs2-tools/o2monitor/Makefile

This makefile builds `o2hbmonitor` as an extra sbin program from `o2hbmonitor.c`. It uses strict warning flags, repository includes, a `VERSION` define, and installs/generates `o2hbmonitor.8`.

The binary has no explicit local library dependencies in this makefile; it links through the common `$(LINK)` rule with standard libc/system dependencies.
