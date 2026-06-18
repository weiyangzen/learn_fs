# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/rt.h

## Role

`rt.h` defines real-time dispatcher class internal structures.

## Data Structures

`rtdpent_t` is one real-time dispatcher parameter table entry with global priority and default quantum.

`rtproc_t` is the real-time class-specific per-thread/process scheduling state:
- assigned quantum and time remaining.
- RT class priority.
- flags.
- time-quantum signal.
- associated thread pointer.
- next/previous links.

The defined flag is `RTBACKQ`, meaning the process goes to the back of the dispatch queue when preempted.

Under `_KERNEL`, `rtkparms_t` carries kernel RT parameters: priority, quantum, quantum signal, and control flags.

## Research Notes

This is a scheduler-class state header. It is tightly coupled to real-time dispatching and priocntl administration, with `rtpriocntl.h` exposing the user/admin side.
