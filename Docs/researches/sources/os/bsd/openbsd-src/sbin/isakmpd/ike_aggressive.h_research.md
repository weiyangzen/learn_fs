# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/ike_aggressive.h

Declares Aggressive Mode initiator and responder function-pointer arrays:
- `ike_aggressive_initiator[]`
- `ike_aggressive_responder[]`

These arrays are consumed through DOI exchange dispatch to run the correct step handler for each exchange step.
