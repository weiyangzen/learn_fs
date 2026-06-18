# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/container/CloseSubcommand.java

## Purpose
Implements `ozone admin container close`, manually closing a container by ID.

## Important APIs, Types, And Functions
The command extends `ScmSubcommand`, has a required long `containerId` parameter, and calls `ScmClient.closeContainer(containerId)`.

## Control Flow
The base class opens an SCM client; `execute` sends the close RPC and lets exceptions propagate.

## State And Persistence
It mutates SCM/container lifecycle state by requesting a close transition.

## Dependencies And Integration Points
Depends on `ScmClient.closeContainer`, picocli parameter binding, and SCM lifecycle validation.

## Risks And Test Signals
There is no local validation for positive IDs or output on success. Tests should cover invalid IDs, missing ID, already closed/open container behavior, and server-side permission failures.
