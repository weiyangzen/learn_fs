# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/hdds/freon/FakeRatisFollower.java

## Purpose
Test/support fake Ratis follower used by instrumented Freon tests to replace real outgoing Ratis gRPC calls.

## Important APIs, Types, And Functions
Static APIs are `appendEntries(RaftPeerId, StreamObserver<AppendEntriesReplyProto>)` and `requestVote(RaftPeerId, RequestVoteRequestProto)`. It reads optional `RATIS_SIMULATED_LATENCY` from the environment.

## Control Flow
AppendEntries returns a stream observer that tracks the maximum log index seen, derives follower commit from commit info and max index, builds successful append replies, optionally sleeps, and sends replies to the response handler. RequestVote returns a successful vote reply for the candidate term.

## State And Persistence
State is static simulated latency and per-append-stream `maxIndex`. No durable persistence.

## Dependencies And Integration Points
Depends on Apache Ratis protobufs, gRPC stream observer, `RaftPeerId`, and Freon test instrumentation.

## Risks
The fake always succeeds and ignores errors/completion, so it cannot model rejection, term changes, or network failures. `System.out.println` in request vote can pollute test logs. Static latency is process-wide.

## Test Signals
Signals include Freon standalone/follower simulations, append reply match/next index behavior, vote success, and latency-injected benchmark runs.
