# File Research: sources/os/bsd/freebsd-src/sbin/swapon/tests/Makefile

## Summary
Registers the `swapon_test` ATF shell test.

## Main Elements
- Sets `ATF_TESTS_SH=swapon_test`.
- Marks the test as requiring root.
- Includes `bsd.test.mk`.

## Dependencies And Integration
Root is required because the tests create md devices and activate/deactivate swap.
