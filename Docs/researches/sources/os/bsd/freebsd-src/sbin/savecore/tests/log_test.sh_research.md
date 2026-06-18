# File Research: sources/os/bsd/freebsd-src/sbin/savecore/tests/log_test.sh

## Summary
ATF shell test for `savecore` stderr/syslog mirroring behavior under `LOG_PERROR`.

## Main Elements
- Runs `savecore -vC /dev/missing` expecting exit status 1.
- Saves stderr to `savecore.err`.
- Verifies stderr contains a syslog-style missing-device error for `/dev/missing`.

## Dependencies And Integration
Uses ATF shell helpers and `grep -qE`.
