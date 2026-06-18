# File Research: sources/os/plan9/9front/sys/src/cmd/aux/realemu/pit.c

`pit.c` emulates the Intel 8253/8254 programmable interval timer. It supports counter latching, status latching/readback, BCD conversion, gate transitions, low/high/lo-hi access modes, and output modes 0 through 5 including rate generator and square wave variants.

`clockpit` advances three timer channels by a number of PIT cycles, honoring gate and reload behavior. `rpit` reads channel count/status latches or live counts. `wpit` handles control words, readback commands, and channel count writes.

The model is good enough for BIOS and real-mode code timing interactions used by `realemu`.
