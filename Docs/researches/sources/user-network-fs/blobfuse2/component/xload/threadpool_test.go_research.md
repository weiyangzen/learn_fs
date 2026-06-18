## sources/user-network-fs/blobfuse2/component/xload/threadpool_test.go

Purpose: Tests xload thread pool creation, lifecycle, scheduling, and priority handling.

Important APIs and flow: `TestThreadPoolCreate` validates nil returns for invalid constructor arguments and successful creation with a callback. `TestThreadPoolStartStop` starts a two-worker pool and stops it. `TestThreadPoolSchedule` schedules one priority and one regular item. `TestPrioritySchedule` schedules 20 priority and 80 regular items on ten workers, sleeps, then asserts the callback ran 100 times.

State and dependencies: Uses context TODO, atomic callback counters, and real goroutines/channels.

Risks and test signals: Tests are sleep-based and do not cover context cancellation, scheduling after stop, backpressure, callback errors, response channels, or priority ordering guarantees. They demonstrate that workers drain both queues under normal conditions.
