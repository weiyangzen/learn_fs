# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsAdmin.hh

## Purpose
Declares the `XrdCmsAdmin` class, the administrative socket/session object for CMS control, notification, relay, and ARE event handling.

## Important APIs, Types, and Functions
Public API includes `InitAREvents`, `Login`, `MonAds`, `setSync`, `Notes`, `Relay`, `RelayAREvent`, `Send`, and `Start`. Private API covers event addition, alternate data-server setup, VNID checking, ADS connection, and command-specific handlers.

## Control Flow
The class is used as a per-connection handler for admin sessions and as a holder of static relay/event queues shared by background threads. `Start()` and static thread entry points in the implementation drive the lifecycle.

## State and Persistence Behavior
Static members hold ARE callback/queue state, startup sync, mutexes, semaphore, and primary-online status. Instance members hold the `XrdOucStream`, role string, allocated server name, and primary marker.

## Dependencies and Integration Points
Includes CMS protocol/RR data, OSS stat info callback type, stream parsing, and pthread wrappers. Forward-declares sockets and token lists. It is integrated by `cmsd` startup and manager/server control paths.

## Risks and Edge Cases
The class mixes static global state and per-session state; tests need isolation or explicit resets. `Sname` is heap-owned and freed in the destructor. Static API is not namespaced under `XrdCms`, unlike some implementation globals.

## Test Signals
Compile tests should catch protocol and callback ABI drift. Unit or harness tests should instantiate sessions with mock streams/sockets and verify static state transitions.
