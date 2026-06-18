# sources/object-store/daos/src/engine/srv_cli.c

## Purpose
`srv_cli.c` lets server code run DAOS client tasks from inside the engine. It provides a per-xstream TSE scheduler progress ULT and a helper to schedule tasks synchronously or asynchronously.

## Important APIs, Types, and Functions
The exported functions are `dsc_task_run(tse_task_t *task, tse_task_cb_t retry_cb, void *arg, int arg_size, bool sync)` and `dsc_scheduler(void)`. Private helpers are `dsc_progress`, `dsc_progress_start`, and `dsc_task_comp_cb`.

## Control Flow
Before running a client task, `dsc_task_run` ensures the current xstream has a DSC progress ULT. In synchronous mode it creates an `ABT_eventual` and registers `dsc_task_comp_cb` to copy task result into the eventual. If a retry callback is supplied, it is registered last so it runs first on completion. The task is scheduled with `tse_task_schedule`; synchronous callers wait on the eventual and return the task result.

## State and Persistence Behavior
The state is per-xstream: `dx->dx_dsc_started` prevents duplicate progress ULT creation, and `dx->dx_sched_dsc` is the TSE scheduler initialized in `srv.c`. No persistence is performed. Task completion status moves through task fields and optional Argobots eventual storage.

## Dependencies and Integration Points
This file depends on DAOS client task/event APIs, server xstream metadata, Argobots eventuals, and `dss_ult_create`. It is used by server subsystems that need to call client-layer APIs, such as recovery paths, while continuing to progress their TSE scheduler.

## Risks
The file notes that client APIs may acquire global pthread locks and block an entire xstream. Progress ULT lifetime is tied to xstream shutdown and loops until `dss_xstream_exiting`. Synchronous waits require the progress ULT to run; failures during callback registration must complete the task and free eventuals correctly. Callback ordering is deliberate for retry behavior.

## Test Signals
Tests should cover async and sync task execution, progress ULT single-start behavior, task scheduling failure, completion callback result propagation, retry callback ordering, eventual create/wait failures, and shutdown while the progress loop is active.
