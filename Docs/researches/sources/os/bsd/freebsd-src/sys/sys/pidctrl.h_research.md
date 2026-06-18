# File Research: sources/os/bsd/freebsd-src/sys/sys/pidctrl.h

This header defines a simple integer proportional-integral-derivative controller for kernel daemons and resource regulation. The comments describe its goal: replace threshold-based high/low water behavior that creates bursty sawtooth activity with smoother adaptive control.

`struct pidctrl` stores current/old error, integral, derivative, last input/output, last sampling tick, plus tunable configuration: setpoint, interval, integral bound, and divisors for proportional/integral/derivative gains. Gains are represented as inverse integer divisors to avoid floating point. Defaults are provided for proportional, integral, derivative, and bound factors.

The API includes initialization, sysctl initialization, a classic controller that can produce negative output for bidirectional control loops, and a daemon-oriented controller whose output is positive work required to reduce an input variable. The daemon variant supports repeated calls in overload cases but warns that stable control depends on interval behavior and tuning.

Filesystem relevance is workload regulation: reclaimers, flushers, or maintenance daemons can use this style of controller to avoid latency spikes caused by abrupt threshold-driven work.
