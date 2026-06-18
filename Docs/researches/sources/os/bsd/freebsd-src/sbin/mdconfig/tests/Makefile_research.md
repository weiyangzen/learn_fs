# File Research: sources/os/bsd/freebsd-src/sbin/mdconfig/tests/Makefile

## Summary
Registers the `mdconfig_test` ATF shell test.

## Main Elements
- Sets `ATF_TESTS_SH=mdconfig_test`.
- Marks the test as requiring root through `TEST_METADATA.mdconfig_test+= required_user="root"`.
- Includes `bsd.test.mk`.

## Research Notes
Root is required because the tests create and destroy md(4) devices.
