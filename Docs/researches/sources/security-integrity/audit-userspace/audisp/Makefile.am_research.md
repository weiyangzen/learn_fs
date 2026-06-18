## sources/security-integrity/audit-userspace/audisp/Makefile.am

Purpose: build fragment for audit dispatcher static libraries.

It builds `libdisp.la` from dispatcher/config/list sources and `libqueue.la` from queue sources, links against common/libaudit and pthread, includes plugin tests, and exports internal headers. State is static noinst libraries. Dependencies are top-level libaudit/common, queue implementation, pthread, and compiler flags. Risks include static library boundaries hiding ABI issues and plugin headers consumed across directories. Test signal is dispatcher tests under `audisp/test` and full build.
