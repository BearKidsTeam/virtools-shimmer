cmake_minimum_required(VERSION 3.10.0)

project(CK2Shim VERSION 0.0 LANGUAGES CXX)

if (NOT ${MSVC})
	message(FATAL_ERROR "MSVC is required to build this shim.")
endif()

if (NOT ${MAKE_GENERATOR_PLATFORM} MATCHES "Win32")
	message(FATAL_ERROR "64bit Virtools isn't real.")
endif()

find_path(VIRTOOLS_INCLUDE_DIR CKTypes.h)
find_path(VIRTOOLS_LIBS_DIR VxMath.lib)

if (${VIRTOOLS_INCLUDE_DIR} MATCHES "NOTFOUND" OR ${VIRTOOLS_LIBS_DIR} MATCHES "NOTFOUND")
	message(FATAL_ERROR "Cannot find Virtools SDK.")
endif()

set(CMAKE_INCLUDE_CURRENT_DIR ON)

add_subdirectory(src)
