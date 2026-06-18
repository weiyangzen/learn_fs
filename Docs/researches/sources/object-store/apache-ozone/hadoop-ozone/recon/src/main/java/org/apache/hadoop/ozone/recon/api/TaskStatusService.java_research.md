<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/TaskStatusService.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/TaskStatusService.java

## Purpose

`TaskStatusService` is a JAX-RS endpoint for exposing the last recorded status rows for Recon background tasks.

## Important APIs and Types

The class is mounted at `/task` and produces JSON. `GET /task/status` calls `ReconTaskStatusDao.findAll()` and returns a list of generated `ReconTaskStatus` POJOs.

## Control Flow

Requests enter `getTaskStats`, read all rows from `RECON_TASK_STATUS` through the injected DAO, and return HTTP 200 with the raw result list. There is no filtering, pagination, readiness check, or explicit exception handling.

## State and Persistence

The endpoint holds an injected `ReconTaskStatusDao`. It is read-only from the endpoint perspective, but data comes from Recon's SQL task status table populated by background tasks.

## Dependencies and Integration Points

It integrates with jOOQ-generated DAO/POJO classes under `org.apache.ozone.recon.schema.generated.tables` and the Recon task framework that updates task status rows.

## Risks and Edge Cases

The endpoint returns every task row without paging, so response size grows with task count. DAO failures propagate as generic server errors. Because the generated POJO shape is exposed directly, schema changes can affect clients.

## Test Signals

Tests should verify DAO delegation, JSON serialization of `ReconTaskStatus`, empty-table behavior, DAO exception mapping, and route registration at `/task/status`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/TaskStatusService.java -->
