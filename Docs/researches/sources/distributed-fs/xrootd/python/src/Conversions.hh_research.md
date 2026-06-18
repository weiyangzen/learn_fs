# sources/distributed-fs/xrootd/python/src/Conversions.hh

## Purpose
This header centralizes conversion of XrdCl C++ response objects into Python dictionaries, lists, tuples, booleans, and bytes for PyXRootD.

## Important APIs, Types, and Functions
`ConvertType<T>` dispatches through `PyDict<T>::Convert`. Specializations cover `XRootDStatus`, `ProtocolInfo`, `StatInfo`, `StatInfoVFS`, `DirectoryList`, `HostList`, `LocationInfo`, `Buffer`, `ChunkInfo`, `VectorReadInfo`, `PropertyList`, `std::deque<PropertyList>`, `std::vector<std::string>`, `std::vector<XAttrStatus>`, and `std::vector<XAttr>`.

## Control Flow
Each converter allocates Python containers, extracts fields from XrdCl objects, and builds Python values. Buffer/chunk converters return bytes. `ChunkInfo` and `VectorReadInfo` converters delete the backing chunk buffers after building Python bytes, making conversion part of memory cleanup. Host-list conversion ensures `URLType` is ready and wraps host URLs as Python URL objects.

## State and Persistence
No persistent state is stored. Some converters have ownership side effects by freeing XrdCl-allocated buffers. All output state is newly allocated Python objects.

## Dependencies and Integration Points
Depends on Python C API, `PyXRootDURL.hh`, `Utils.hh`, XrdCl response headers, property lists, and extended attribute types. It is used throughout file, filesystem, copy, async, and progress-handler code.

## Risks and Test Signals
Reference ownership is subtle: several converters use `Py_BuildValue` with `N` or `O` and then decref temporary objects. Buffer ownership conventions must match XrdCl expectations, especially for async vector reads. `PyDict<XrdCl::AnyObject>` always returns `None`, so methods using that type expose only status. Tests should validate exact Python shapes for every XrdCl operation, memory safety under vector reads/chunk reads, host-list URL conversion, and property-list copy results.
