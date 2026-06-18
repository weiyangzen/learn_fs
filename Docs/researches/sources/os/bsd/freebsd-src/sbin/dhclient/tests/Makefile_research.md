# File Research: sources/os/bsd/freebsd-src/sbin/dhclient/tests/Makefile

## Purpose
Builds dhclient ATF tests.

## Main Elements
- Sets `.PATH` to parent dhclient directory.
- Defines shell ATF test `pcp` and marks it exclusive because tests share an IP.
- Defines plain C test `option-domain-search_test` with source list including dhclient support files and `fake.c`.
- Adds include path to parent and links `libutil`.
- Includes `bsd.test.mk`.

## Dependencies And Integration
Integrates with FreeBSD test infrastructure and builds unit coverage for domain-search parsing plus an integration shell test for normal/PCP interface DHCP behavior.

## Risk Notes
The C test links selected production sources with fake diagnostics/handlers, so source list drift can break test builds.
