# sources/user-network-fs/samba/source3/nmbd/wscript_build

Purpose: declares the Samba3 `nmbd` binary build target and all source files that compose the NetBIOS name service/browser daemon.

Important build API: uses Waf helper `bld.SAMBA3_BINARY('nmbd', ...)`. It conditionally sets `nmbd_cflags` to `-Wno-error=stringop-overflow` when `HAVE_WNO_ERROR_STRINGOP_OVERFLOW` is configured. The source list includes packet handling, browser/election/database modules, WINS proxy/server code, logon processing, async DNS, and `nmbd_workgroupdb.c`.

State and persistence: no runtime state; it affects build graph state by selecting inputs, dependencies, flags, and install path.

Dependencies and integration: links against `talloc`, `tevent`, `smbconf`, `libsmb`, and `CMDLINE_S3`, and installs into `${SBINDIR}`. The broad source list means changes here can include or exclude major nmbd subsystems from the daemon.

Risks: build-file drift can silently omit a daemon module or hide compiler diagnostics globally for the target. The conditional warning downgrade is compiler-feature gated but still broad for all nmbd sources.

Test signals: configure/build should verify `nmbd` is produced, links all named objects, and installs to the expected sbin location. Dependency changes should be validated by a clean build, not just incremental compilation.
