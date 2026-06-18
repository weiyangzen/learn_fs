# File Research: sources/virtualization/spdk/app/trace_record/Makefile

This makefile builds `spdk_trace_record` from `trace_record.c`. It includes SPDK common rules, links the `util` and `log` libraries, and then uses the standard C application build include `mk/spdk.app.mk`.

The install and uninstall targets delegate to SPDK's standard app install macros. The linked library list matches the source: it uses SPDK trace structures and utility helpers, but it is a standalone recorder rather than a full event-framework app.
