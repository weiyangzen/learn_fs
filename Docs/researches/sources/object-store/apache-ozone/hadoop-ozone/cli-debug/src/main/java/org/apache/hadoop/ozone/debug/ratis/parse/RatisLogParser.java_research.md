# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/ratis/parse/RatisLogParser.java

Purpose: `RatisLogParser` implements `ozone debug ratis parse`, selecting a state-machine decoder for OM, SCM, datanode, or generic Ratis log output.

Important APIs and types: It extends `BaseLogParser`, implements `Callable<Void>`, has `--role`, and uses `OMRatisHelper`, `SCMRatisRequest`, `ContainerStateMachine`, `StateMachineLogEntryProto`, and a dummy `RaftGroupId` for datanode log decoding.

Control flow: `call` lowercases `role`, prints the selected mode, and calls `parseRatisLogs` with the appropriate converter: OM, SCM, datanode container command decoder, or null for generic output. `smToContainerLogString` wraps the datanode converter with the dummy pipeline ID.

State and persistence behavior: The command reads the segment file and prints decoded entries. It has no durable state.

Dependencies and integration points: It is registered by `RatisDebug` and relies on Ratis tooling plus Ozone component-specific state-machine log translators.

Risks: Unknown roles silently fall back to generic parsing. Datanode parsing uses a dummy pipeline ID and null context, so output is diagnostic rather than exact runtime replay. Failures are swallowed by `BaseLogParser`.

Test signals: Tests should cover role dispatch, converter output for representative entries, generic fallback, datanode dummy ID notice, and segment parsing failure behavior.
