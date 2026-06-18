# sources/distributed-fs/xrootd/src/XrdCeph/XrdCephBuffers/XrdCephReadVBasic.hh

Purpose: declares the default/basic readv adapter for XrdCeph.

Important APIs/types/functions: `XrdCephReadVBasic` implements `IXrdCephReadVAdapter::convert`; configurable member defaults are `m_minSize = 2 MiB` and `m_maxSize = 16 MiB`; counters `m_usedBytes` and `m_wastedBytes` track efficiency.

Control flow: convert groups input extents into larger requests constrained by the min/max sizes, leaving remapping to the caller.

State and persistence: in-memory stats only, logged on destruction.

Dependencies and integration points: includes `BufferUtils.hh` and `IXrdCephReadVAdapter.hh`. Compiled into the XrdCeph module as one readv strategy.

Risks: size thresholds are protected members, not constructor parameters, so tuning requires subclassing/source edits. No explicit requirement that input extents are sorted is documented in the interface.

Test signals: conversion behavior around 2 MiB and 16 MiB thresholds, counter accumulation, destructor logging, and use through base adapter pointer.
