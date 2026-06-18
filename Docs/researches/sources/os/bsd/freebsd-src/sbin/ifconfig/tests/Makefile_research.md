# File Research: sources/os/bsd/freebsd-src/sbin/ifconfig/tests/Makefile

This Makefile defines ATF shell tests for the ifconfig directory. It includes the tests `ifconfig` and `inet6`.

It also declares `NETBSD_ATF_TESTS_SH= nonexistent_test`, preserving a NetBSD test harness convention. Test metadata requests execution in a VNET jail with raw sockets: `execenv="jail"` and `execenv_jail_params="vnet allow.raw_sockets"`.

The file includes `<netbsd-tests.test.mk>` and `<bsd.test.mk>`, integrating the tests into the FreeBSD build/test framework.
