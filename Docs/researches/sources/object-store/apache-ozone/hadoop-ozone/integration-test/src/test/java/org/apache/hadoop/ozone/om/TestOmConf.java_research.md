# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestOmConf.java

Purpose: This small unit-style integration test verifies that `OzoneManagerRatisServerConfig.logAppenderWaitTimeMin` is translated correctly from `OzoneConfiguration` into the Ratis `RaftProperties` used by OM Ratis.

Important APIs and types: The file uses `OzoneConfiguration`, `OzoneManagerRatisServerConfig`, `OzoneManagerRatisServer.newRaftProperties`, `RaftProperties`, `RaftServerConfigKeys.Log.Appender.waitTimeMin`, and Ratis `TimeDuration`.

Control flow: `testConf` creates a fresh configuration, reads the typed OM Ratis config object, asserts the default wait-time minimum is zero, and calls `assertWaitTimeMin` to verify the generated Ratis property is `TimeDuration.ZERO`. It then sets the typed value to `1`, writes the object back to the configuration with `setFromObject`, and verifies the generated Ratis property becomes one millisecond.

State and persistence behavior: There is no filesystem or DB persistence. State is limited to the in-memory configuration object and derived Ratis properties. The test protects config serialization/deserialization between Ozone's typed config object and the Ratis property namespace.

Dependencies and integration points: It covers OM Ratis server configuration plumbing, especially the conversion path used during OM Ratis server startup when `newRaftProperties` is built from Ozone config plus port and storage directory inputs.

Risks: The test only checks one Ratis property and uses a dummy directory/port, so it does not validate full Ratis startup. It assumes the integer config value is expressed in milliseconds.

Test signals: Signals are exact equality for default typed value `0`, generated wait-time `TimeDuration.ZERO`, generated wait-time `TimeDuration.ONE_MILLISECOND` after setting the typed config to `1`, and the Ratis property key reported in assertion messages.
