# sources/distributed-fs/xrootd/src/XrdCl/XrdClResponseJob.hh

## Purpose

This header defines `ResponseJob`, a `JobManager` task that invokes a user `ResponseHandler` asynchronously with status, response object, and host-list pointers.

## Important APIs, Types, And Functions

`ResponseJob` stores `ResponseHandler *pHandler`, `XRootDStatus *pStatus`, `AnyObject *pResponse`, and `HostList *pHostList`. Its `Run(void*)` calls `pHandler->HandleResponseWithHosts(pStatus, pResponse, pHostList)` and deletes the job object.

## Control Flow

Producer code allocates a `ResponseJob` and queues it on `JobManager`. When a worker runs it, ownership of response payload pointers is effectively handed to the handler according to `HandleResponseWithHosts` conventions, and the job self-deletes.

## State And Persistence Behavior

State is transient and owned by the job until `Run`. The job does not persist data. It does not delete the payload pointers itself, so handler ownership rules are critical.

## Dependencies And Integration Points

The header depends on `XrdClJobManager.hh` and `XrdClXRootDResponses.hh`. It is a common bridge between internal async completion and public response callback delivery.

## Risks And Edge Cases

Raw pointers must remain valid until the job runs. A null handler would crash. Because the job deletes itself, it must be heap-allocated and must not be reused after queuing. Handler exceptions, if any, are not caught here.

## Test Signals

Tests should queue a `ResponseJob` with a fake handler, verify exact pointer delivery, confirm self-deletion under leak checks, and exercise null/invalid pointer behavior only under guarded negative tests.
