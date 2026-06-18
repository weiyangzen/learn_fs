# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/audio/audio_driver.h

## Purpose

`audio/audio_driver.h` defines the kernel driver-facing interface to the illumos audio framework.

## Engine Interface

`audio_engine_ops_t` version 2 contains callbacks for engine open/close, start/stop, frame count, format, channel count, sample rate, DMA cache sync, hardware queue length, optional per-channel buffer layout, and optional play-ahead policy. Open returns actual fragment/buffer values through pointer hints.

## Device and Engine API

Drivers can initialize/finalize devops, allocate/free audio devices, set description/version/info strings, allocate/free engines, set/get engine-private data, add/remove engines, register/unregister devices, suspend/resume devices, and emit warnings. Debug byte/word/dword dump helpers are also declared.

Engine flags identify input/output capability and framework-managed open modes such as output/input, exclusive use, and nonblocking open.

## Controls

The header defines control read/write callback types and APIs to add/delete controls, add synthetic PCM soft volume, notify control updates, and read/write controls through driver callbacks.

## Research Notes

This is the primary integration contract for audio device drivers. Correct use requires stable engine callbacks and careful DMA buffer synchronization.
