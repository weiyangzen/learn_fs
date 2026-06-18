# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/protocol/commands/DeleteBlockCommandStatus.java

Purpose: specialized command status carrying block deletion acknowledgement details.

Important APIs and functions: constructor adds optional `ContainerBlocksDeletionACKProto` to the base command status. `setBlocksDeletionAck` updates the acknowledgement. `getFromProtoBuf` uses the nested builder to restore status plus block deletion ack. `getProtoBufMessage` serializes base status fields and includes block deletion ack and message when present. `DeleteBlockCommandStatusBuilder` extends the base builder with `setBlockDeletionAck`.

Control flow and state: ack is mutable after construction. Other status fields are inherited from `CommandStatus`.

Dependencies and integration: used when datanodes report results of `DeleteBlocksCommand` transactions back to SCM.

Risks and test signals: ack omission can lose per-transaction deletion results. Tests should cover proto round trip with and without ack, message propagation, status transitions inherited from base class, and builder covariance.
