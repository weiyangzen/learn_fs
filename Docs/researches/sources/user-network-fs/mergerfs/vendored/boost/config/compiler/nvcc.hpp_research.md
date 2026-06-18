<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/compiler/nvcc.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/config/compiler/nvcc.hpp

## Purpose
This adapter applies Boost.Config corrections when code is compiled through NVIDIA NVCC.

## Important APIs, Types, And Control Flow
It defines `BOOST_COMPILER` as `nvcc` plus `CUDART_VERSION`, marks `BOOST_GPU_ENABLED` as `__host__ __device__`, and disables features known to be problematic for CUDA compilation: `BOOST_NO_CXX11_VARIADIC_MACROS`, `BOOST_NO_CXX11_HDR_INITIALIZER_LIST`, `BOOST_NO_CXX11_HDR_CHRONO`, `BOOST_NO_CXX11_HDR_CODECVT`, `BOOST_NO_CXX11_HDR_ATOMIC`, and in device compilation, `BOOST_NO_CXX14_DIGIT_SEPARATORS`. If `__CUDACC_VER_MAJOR__` is available it conditionally disables extended lambdas, `std::allocator`, C++17 fold expressions, `if constexpr`, inline variables, structured bindings, and auto non-type template parameters by CUDA and `__cplusplus` thresholds.

## State And Persistence
It is macro-only and has no runtime state.

## Dependencies And Integration Points
It depends on CUDA version macros and NVCC host/device markers. It overlays host compiler configs by correcting features that host compilers may report but NVCC cannot compile reliably.

## Risks And Test Signals
Risks include CUDA version skew, host compiler feature leakage, and device-pass restrictions differing from host-pass restrictions. Test signals are NVCC compile tests for host and `__CUDA_ARCH__` device paths across CUDA versions, especially initializer lists, chrono, atomics, generic/extended lambdas, and C++17 constructs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/config/compiler/nvcc.hpp -->
