# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/addname.c

Implements NBNS name registration through `nbnsaddname`.

Key behavior:
- Builds a name registration request with `nbnsmessagenameregistrationrequestnew`.
- Uses `NbnsAlarm` plus a transaction response channel in an `Alt` loop.
- Retries `NbnsRetryBroadcast` times with `NbnsTimeoutBroadcast` timeout.
- Accepts only NBNS registration responses and returns the NBNS rcode, `0`, or `-1`.

Interactions:
- Depends on `message.c`, `nbns.c`, `alarm.c`, and `nbnsconv.c`.
- Broadcast mode is selected when `serveripaddr == nil`.

Notable details:
- Frees the transaction before leaving the response loop.
- Frees both request and response messages before returning.
