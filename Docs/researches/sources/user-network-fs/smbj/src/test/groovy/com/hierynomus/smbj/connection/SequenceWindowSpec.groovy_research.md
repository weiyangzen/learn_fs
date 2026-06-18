# sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/smbj/connection/SequenceWindowSpec.groovy
# sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/smbj/connection/SequenceWindowSpec.groovy

Purpose: tests SMB2 message-id/credit sequence allocation. It exercises `SequenceWindow` behavior for reserving available credits, expanding with granted credits, exhaustion behavior, and window accounting.

State and persistence: in-memory counters/window state only. Dependencies are the connection sequence-window class and Spock. Integration point is SMB2 credit-based flow control and message-id assignment for all requests. Risks covered include off-by-one IDs, over-allocation, failure to honor credits, and incorrect available-count reporting. Test signal is focused and important for concurrency and high-throughput SMB operations.
