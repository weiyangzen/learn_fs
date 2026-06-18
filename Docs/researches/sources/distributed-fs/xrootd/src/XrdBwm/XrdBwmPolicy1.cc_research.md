# sources/distributed-fs/xrootd/src/XrdBwm/XrdBwmPolicy1.cc

Purpose: implements the built-in simple slot-count BWM policy with separate incoming and outgoing concurrency limits.

Important APIs/types/functions: constructor initializes slot counts and `refID`; `Dispatch` waits for queued work and moves it to executing; `Done` releases active slots or cancels queued refs; `Schedule` grants, queues, or rejects requests; `Status` reports counts.

Control flow: `Schedule` creates a `refReq`, decrements available slots and adds to Xeq when capacity exists, queues when capacity is exhausted but max slots are nonzero, or rejects when that direction is disabled. `Dispatch` checks incoming first, then outgoing, and waits on `pSem` if no queued request can run. `Done` removes from active first and posts the semaphore if a slot becomes newly available.

State and persistence: all state is in `theQ[In/Out/Xeq]`, the semaphore, mutex, and monotonically increasing `refID`. There is no persistence.

Dependencies and integration points: implements `XrdBwmPolicy` for default use by `XrdBwmConfig`.

Risks: `refSch::Add` appears to link new nodes through `rP->Next = Last`, which creates a reverse/backward chain while `Next()` consumes from `First`; after more than one queued element, traversal/order behavior is suspect. `refID` can overflow. Incoming always has dispatch priority over outgoing.

Test signals: maxslots zero rejection, immediate grant, FIFO behavior for multiple queued requests, cancellation from queued/active lists, semaphore wakeups on slot release, and status count accuracy.
