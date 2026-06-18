# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/ScmConfig.java

## Purpose
Defines annotated configuration fields for the SCM service that are loaded through HDDS's typed configuration framework. It covers Kerberos identity, unknown-container handling, Ratis and EC pipeline choose policy classes, block deletion rate/interval, and deletion transaction map limit.

## Important APIs, Types, And Functions
`ScmConfig` extends `ReconfigurableConfig` and is annotated with `@ConfigGroup(prefix = "hdds.scm")`. `@Config` fields include `principal`, `keytab`, `action`, `pipelineChoosePolicyName`, `ecPipelineChoosePolicyName`, `blockDeletionLimit`, `blockDeletionInterval`, and `transactionToDNsCommitMapLimit`. Getters/setters expose each value. Nested `ConfigStrings` preserves legacy Kerberos key constants for `KerberosInfo`.

## Control Flow
The configuration framework instantiates and populates this class from keys/defaults, then runtime services read getters or update reconfigurable values such as block deletion limit.

## State And Persistence
Instances hold in-memory configuration. Values originate from persisted configuration files or dynamic reconfiguration state; this class itself does not write persistence.

## Dependencies And Integration Points
Depends on `org.apache.hadoop.hdds.conf` annotations and integrates with SCM security login, pipeline policy factory loading, block deleting service scheduling, and dynamic configuration.

## Risks And Test Signals
Class-name values are free-form strings and fail later at policy instantiation. Unknown-container action is also unvalidated here. Tests should cover config default binding, dynamic reconfiguration, invalid policy class handling, and block deletion interval/limit behavior.
