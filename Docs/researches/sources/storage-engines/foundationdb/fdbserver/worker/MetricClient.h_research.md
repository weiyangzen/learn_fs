# sources/storage-engines/foundationdb/fdbserver/worker/MetricClient.h

## Purpose
`MetricClient.h` declares the abstract metric emission interface and the UDP implementation used by worker metric logging.

## Important APIs, Types, And Functions
`IMetricClient` stores a `MetricsDataModel` and declares virtual `send(MetricCollection*)`. `UDPMetricClient` owns a UDP socket future, native socket fd, msgpack buffer, destination address/port, and private `send_packet`. It exposes a constructor and `send` override. `MAX_OTELSUM_PACKET_SIZE` is set to 75 percent of UDP max packet size to avoid oversize OTLP sum batches.

## Control Flow
The header defines no behavior beyond virtual dispatch. Construction and emission behavior live in `MetricClient.cpp`.

## State And Persistence Behavior
There is no persistence. State is process-local and reused across metric emission intervals.

## Dependencies And Integration Points
The header includes UDP socket, Msgpack, TDMetric, and Flow network types. `MetricLogger.actor.cpp` instantiates `UDPMetricClient` from `runMetrics()`.

## Risks And Test Signals
The base and derived classes both contain a `model` member, which can be confusing because the derived member shadows the protected base member. Packet sizing constants and socket lifetime must stay aligned with Flow network behavior.
