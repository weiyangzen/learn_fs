# sources/security-integrity/cryfs/old-cpp/src/fspp/fstest/testutils/TimestampTestUtils.h

Purpose: shared timestamp assertion framework for fspp tests, including reusable expectations and a builder that repeats checks under all supported atime policies.

Important APIs/types/functions: `TimestampTestUtils`, `TimestampUpdateExpectation`, `EXPECT_OPERATION_UPDATES_TIMESTAMPS_AS` overloads, `EXPECT_*_TIMESTAMP_BETWEEN`, `stat`, `xSecondsAgo`, `ensureNodeTimestampsAreOld`, `TestBuilder`, and static expectation lambdas.

Control flow: captures old stat, waits until the clock progresses, records operation bounds, executes the operation, captures new stat, and applies each expectation. Builder methods reset the filesystem with noatime, strictatime, relatime, nodiratime+relatime, or nodiratime+strictatime.

State and persistence behavior: resets discard prior fixture state between atime modes. Timestamp comparison depends on filesystem metadata persistence and nanosecond-resolution clock progress.

Dependencies and integration points: depends on `cpputils::time`, `cpputils::stat`, `FileSystemTest`, fspp `Context`, `Node`, and `OpenFile`.

Risks and test signals: centralizes precise ctime/mtime/atime expectations. Busy-wait clock progression is intentionally fast but can spin under coarse clocks; operation-bound comparisons can be flaky if filesystem timestamp precision is lower than `timespec`.
