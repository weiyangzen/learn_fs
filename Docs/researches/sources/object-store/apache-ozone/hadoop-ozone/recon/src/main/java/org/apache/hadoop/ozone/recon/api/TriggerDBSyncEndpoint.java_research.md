<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/TriggerDBSyncEndpoint.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/TriggerDBSyncEndpoint.java

## Purpose

`TriggerDBSyncEndpoint` exposes manual trigger and status APIs for Recon's OM and SCM DB synchronization flows.

## Important APIs and Types

Endpoints include `GET /triggerdbsync/om`, `POST /triggerdbsync/scm/snapshot`, `GET /triggerdbsync/scm/snapshot/status`, and `POST /triggerdbsync/scm/snapshot/cancel`. It uses `OzoneManagerServiceProvider` and `ReconStorageContainerManagerFacade`.

## Control Flow

The OM trigger calls `triggerSyncDataFromOMImmediately` and returns HTTP 200. The SCM snapshot trigger calls `reconScm.triggerReconDbSyncWithScm()` and returns the facade result. Status and cancel similarly call the facade and return its response object.

## State and Persistence

The endpoint itself is stateless. It triggers background synchronization that can update Recon's OM/SCM metadata stores and reads/cancels SCM snapshot sync state from the facade.

## Dependencies and Integration Points

It integrates with Recon's OM service provider and SCM facade, and is likely intended for operational/admin use.

## Risks and Edge Cases

There is no explicit error handling; provider/facade exceptions propagate through JAX-RS. The OM operation is exposed as GET despite causing side effects, which can surprise caches or automated probes.

## Test Signals

Tests should assert endpoint-to-provider delegation, side-effect behavior, facade response propagation, exception mapping, and authorization/route configuration.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/TriggerDBSyncEndpoint.java -->
