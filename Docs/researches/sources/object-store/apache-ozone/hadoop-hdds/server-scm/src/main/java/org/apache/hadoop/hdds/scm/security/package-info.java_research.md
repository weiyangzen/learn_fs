# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/security/package-info.java

Purpose: This descriptor identifies the SCM security package. The package contains code for SCM-issued certificates, root CA rotation, secret-key state, and related background services.

Important APIs and types: Important package members in this subset include `RootCARotationHandler`, `RootCARotationHandlerImpl`, `RootCARotationManager`, `RootCARotationMetrics`, `ScmSecretKeyStateBuilder`, and `SecretKeyManagerService`. Nearby package code also includes SCM security protocol implementations and certificate authority integration.

Control flow: The package participates in SCM startup and leader lifecycle. Certificate and key services generally run only on the leader or through Ratis proxies so that replicated state remains ordered.

State and persistence behavior: Package implementations persist security material to SCM certificate/key directories, SCM storage configuration, local secret-key stores, and SCM metadata tables. This file itself has no state.

Dependencies and integration points: The package integrates HDDS security configuration, X.509 certificate clients and servers, SCM HA/Ratis, SCM service management, and Hadoop metrics.

Risks: Package-level documentation can become stale relative to concrete security workflows. Root CA rotation and secret-key rotation are high-impact paths because IO, crypto, and HA ordering failures can force SCM shutdown.

Test signals: Tests should focus on concrete security services, especially idempotence under Ratis replay, leader transitions, and persistence recovery.
