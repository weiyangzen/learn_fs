# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/lwp_timer_impl.h

## Role

Private kernel implementation state for LWP timed waits/sleeps.

## Structure

Includes thread, lwp, time, and systm headers; defines `lwp_timer_t` with target thread, user timespec pointer, requested time, timecheck flags, immediate-timeout flag, error field, and callout ID. Kernel builds declare copyin/enqueue/dequeue/copyout helpers.

## Dependencies And Consumers

Consumed by kernel LWP timer code. Depends on `kthread_t`, `timespec_t`, `callout_id_t`, and `clock_t`.

## Important Details

The state bridges user timespec copyin/copyout with kernel callout scheduling. `lwpt_id` tracks the scheduled callout for dequeue/cancel paths.

## Research Notes

Read completely: 61 lines, 1647 bytes.
