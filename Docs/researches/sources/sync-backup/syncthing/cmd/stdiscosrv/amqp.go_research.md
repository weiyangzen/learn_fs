# sources/sync-backup/syncthing/cmd/stdiscosrv/amqp.go

Purpose: provides optional AMQP fanout replication for the discovery server database.

Important APIs/types/functions: `amqpReplicator`, `newAMQPReplicator`, `amqpSender`, `amqpReceiver`, `amqpSender.Serve`, `amqpSender.send`, `amqpReceiver.Serve`, `amqpChannel`, and `amqpConsume`.

Control flow: `newAMQPReplicator` creates a Suture service containing a sender and receiver. The sender consumes buffered replication records, marshals protobuf messages, and publishes them to the `discovery` fanout exchange with `AppId` set to the local client ID. The receiver declares/binds an exclusive transient queue, ignores messages whose `AppId` is local, unmarshals records, parses the device ID from bytes or legacy string form, and merges records into the database.

State and persistence: the sender has a buffered outbox. Replication itself is transient AMQP fanout; durable state remains in the discovery database. Sender drops messages rather than blocking if the outbox is full.

Dependencies/integration: depends on RabbitMQ AMQP 0-9-1, generated `discosrv` protobufs, `protoutil`, Syncthing `protocol.DeviceID`, the local `database` interface, Suture, and replication Prometheus counters.

Risks and test signals: the exchange and queue are non-durable, so replication does not survive broker restart and relies on the local database flush/S3 backup for persistence. Receiver returns on malformed protobuf or database merge errors, relying on supervisor restart. No direct AMQP tests are present in this subset.
