# sources/distributed-fs/xrootd/src/XrdCl/XrdClLocalFileTask.hh

## Purpose

This header declares `XrdCl::LocalFileTask`, a `Job` subclass that packages a local-file operation result for asynchronous response delivery.

## Important APIs, Types, And Functions

The class exposes a constructor taking `XRootDStatus*`, `AnyObject*`, `HostList*`, and `ResponseHandler*`, a destructor, and `Run(void*)`. Private members retain those four pointers until the job runs.

## Control Flow

`LocalFileHandler` creates this job after local operations that should behave like normal asynchronous XrdCl operations. `JobManager` later calls `Run`, which is implemented in the `.cc` file.

## State And Persistence

All state is transient response state. The header establishes raw-pointer ownership passing from the producer to the job and then to the response handler or deletion path.

## Dependencies And Integration Points

It includes `XrdClStatus.hh`, `XrdClAnyObject.hh`, `XrdClJobManager.hh`, and `XrdClXRootDResponses.hh`. It integrates with the generic `Job` abstraction and `ResponseHandler` callback API.

## Risks

The ownership contract is implicit and raw-pointer-based. Copying is not disabled in the declaration, so accidental copies would duplicate pointer ownership; the class is only intended for heap allocation and single execution by the job manager.

## Test Signals

Build coverage, static analysis for accidental copies, and job-manager tests that local file tasks deliver or free all payload pointers are the main signals.
