file(GLOB CKSHIM_HEADERS *.h)
file(GLOB CKSHIM_TRIVIAL_IMPL trivial/*.cpp)
file(GLOB CKSHIM_NONTRIVIAL_IMPL nontrivial/*.cpp)

include_directories(${VIRTOOLS_INCLUDE_DIR})
link_directories(${VIRTOOLS_LIBS_DIR})
add_library(cks MODULE
	${CKSHIM_HEADERS}
	${CKSHIM_TRIVIAL_IMPL}
	${CKSHIM_NONTRIVIAL_IMPL}
	dllmain.cpp
)
target_link_libraries(cks VxMath)
