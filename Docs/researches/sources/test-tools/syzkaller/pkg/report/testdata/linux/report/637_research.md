# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/637

## Purpose
This fixture validates a KMSAN USB info leak in `hif_usb_send`, with alternate origin `htc_connect_service`.

## Important APIs, types, and functions
Key frames include `usb_submit_urb`, `hif_usb_send`, `htc_connect_service`, worker context, and KMSAN origin-reporting helpers.

## Control flow
A USB send path submits an URB containing uninitialized data. The origin traces back to HTC service connection setup.

## State and persistence behavior
The fixture persists info-leak metadata, USB submission context, and an alternate origin-based title.

## Dependencies and integration points
It integrates KMSAN info-leak parsing with USB networking/ath9k-style HIF and HTC service stacks.

## Risks and test signals
The parser must title the sink as `hif_usb_send` while retaining the origin alternate. `TYPE: KMSAN-INFO-LEAK` is the oracle.
