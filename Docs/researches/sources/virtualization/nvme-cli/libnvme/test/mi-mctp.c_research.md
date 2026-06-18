# File Research: sources/virtualization/nvme-cli/libnvme/test/mi-mctp.c

## Role

`mi-mctp.c` is a full fake-MCTP transport test for libnvme Management Interface behavior over MCTP sockets. It wraps socket creation, `sendmsg`, `recvmsg`, `poll`, and MCTP tag ioctls so MI/MCTP behavior can be tested without a real endpoint.

## Test Harness

`struct test_peer` stores linear RX and TX buffers from the device perspective. RX is data sent from libnvme to the fake device; TX is data returned from the fake device to libnvme. Buffers include the NVMe-MI message type byte so tests can compare protocol diagrams directly.

The wrapped `sendmsg()` gathers iovecs into `rx_buf`. The wrapped `recvmsg()` either calls a per-test TX callback or synthesizes a minimal response, computes and appends MIC, scatters bytes into iovecs, and clears the TX buffer. `poll()` can be overridden per test. MCTP tag allocation/drop ioctls are simulated when the platform exposes the relevant constants.

## Coverage

Basic negative-path tests cover send errors, no response, receive errors, short responses, poll errors, poll timeout, and invalid response sizing.

MI/Admin response tests cover MI status errors, admin-over-MI errors, every 4-byte-aligned response size up to 4096 plus header, unaligned controller lists, and direct submit behavior with exact response lengths.

More Processing Required coverage simulates MPR followed by final success for MI and Admin commands, including a quirk where a drive returns an Admin-shaped MPR response. Additional tests validate endpoint timeout use, MPR-provided timeout values, maximum MPR clamping, and zero-MPR fallback.

AEM coverage is extensive. It simulates getting currently enabled events, disabling endpoint-enabled events, enabling host-requested events, receiving asynchronous event occurrence lists, invoking the handler, reading queued events with `libnvme_mi_aem_get_next_event()`, ACK responses, disable flows, invalid API usage, get-enabled behavior, and malformed endpoint responses at several protocol stages.

## Dependencies

- Uses libnvme public and private MI headers.
- Uses Linux MCTP headers or libnvme compatibility headers.
- Uses `utils.h` logging helpers.
- Calls internal CRC helper `libnvme_mi_crc32_update()`.

## Filesystem/Storage Relevance

This is storage-management transport testing. It validates reliability and protocol parsing for NVMe-MI over MCTP, which is relevant to out-of-band storage device management.
