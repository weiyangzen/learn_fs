# File Research: sources/os/plan9/9front/sys/src/9/port/devloopback.c

Purpose: virtual loopback link device `#λ`, providing paired endpoints with configurable delay, byte delay, queue limits, input drop behavior, and deliberate drop rate.

Exposed interface: up to five loopback instances. Each `loopback<n>` has endpoint directories `0` and `1`; each endpoint exposes `ctl`, `status`, `stats`, and `data`. Data written to one endpoint is delivered to the other.

Core implementation: `Loop` owns two `Link`s. Each `Link` has input/output queues, transmission queue, timer, counters, drop/delay settings, and queue limit. `loopbackattach` initializes queues and defaults on first ref. Opening `data` is exclusive per endpoint. Closing one data side hangs up the opposite output and drains/schedules; closing both resets queues and settings.

Packet scheduling: `loopoput` pads a timestamp header, updates counters, queues to the opposite link, and calls `looper`. `pushlink` moves blocks from output queue to delayed transmit queue and then into input queue when their timestamp expires, scheduling a timer for the next event. Delay is `delay0ns + len * delaynns`; drop behavior is controlled by `indrop` and `droprate`.

Dependencies: kernel queues, timers, TOD nanosecond time, block manipulation helpers.

Research notes: important review areas are timer locking, block ownership on drops and queue overflow, close/hangup interactions, timestamp header accounting, and control command validation for negative or extreme delay/limit values.
