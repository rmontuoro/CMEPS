cmake_minimum_required(VERSION 3.7...3.15 FATAL_ERROR)

# Define the CMake project
project(cmeps
  VERSION 1.0.0
  DESCRIPTION  "NUOPC based Community Mediator for Earth Prediction Systems"
  HOMEPAGE_URL "https://escomp.github.io/CMEPS"
  LANGUAGES Fortran)

include(GNUInstallDirs)

if(NOT CMAKE_BUILD_TYPE MATCHES "^(Debug|Release|RelWithDebInfo|MinSizeRel)$")
  message(STATUS "Setting build type to 'Release' as none was specified.")
  set(CMAKE_BUILD_TYPE
      "Release"
      CACHE STRING "Choose the type of build." FORCE)
  set_property(CACHE CMAKE_BUILD_TYPE PROPERTY STRINGS "Debug" "Release" "MinSizeRel" "RelWithDebInfo")
endif()

if(NOT CMAKE_Fortran_COMPILER_ID MATCHES "^(Intel|GNU)$")
  message(WARNING "Compiler not officially supported: ${CMAKE_Fortran_COMPILER_ID}")
endif()

# Append directory that contains CMake Modules
list(INSERT CMAKE_MODULE_PATH 0 ${CMAKE_CURRENT_SOURCE_DIR}/cmake)

# Build options
option(CMEPS_BUILD_STATIC_LIBS "Build CMEPS static library" ON )
option(CMEPS_BUILD_SHARED_LIBS "Build CMEPS shared library" OFF )

# Ensure at least one of CMEPS_BUILD_SHARED_LIBS and CMEPS_BUILD_STATIC_LIBS is set
if(NOT (CMEPS_BUILD_STATIC_LIBS OR CMEPS_BUILD_SHARED_LIBS))
    message(STATUS "Niether CMEPS_BUILD_STATIC_LIBS nor CMEPS_BUILD_SHARED_LIBS is set.  Defaulting to CMEPS_BUILD_STATIC_LIBS=ON")
    set(CMEPS_BUILD_STATIC_LIBS ON CACHE BOOL "Build CMEPS static library" FORCE)
    set(CMEPS_BUILD_STATIC_LIBS ON)
endif()

message(STATUS "Option: CMEPS_BUILD_STATIC_LIBS: ${CMEPS_BUILD_STATIC_LIBS}")
message(STATUS "Option: CMEPS_BUILD_SHARED_LIBS: ${CMEPS_BUILD_SHARED_LIBS}")

find_package(MPI REQUIRED)
find_package(ESMF MODULE REQUIRED)
find_package(PIO REQUIRED COMPONENTS C Fortran)

option(ENABLE_OPENMP "Build CMEPS with OpenMP support" OFF)
if(ENABLE_OPENMP)
  find_package(OpenMP REQUIRED)
endif()

list(APPEND _nems_util_files
  nems/util/shr_abort_mod.F90
  nems/util/shr_log_mod.F90
  nems/util/shr_pio_mod.F90
  nems/util/shr_sys_mod.F90
  nems/util/shr_flux_mod.F90
  nems/util/shr_mpi_mod.F90
  nems/util/glc_elevclass_mod.F90
  nems/util/shr_mem_mod.F90
  nems/util/shr_kind_mod.F90
  nems/util/perf_mod.F90
  nems/util/shr_const_mod.F90)

list(APPEND _mediator_src_files
  mediator/med_phases_restart_mod.F90
  mediator/med_map_mod.F90
  mediator/med_methods_mod.F90
  mediator/med_phases_prep_ice_mod.F90
  mediator/med_phases_history_mod.F90
  mediator/med_phases_prep_glc_mod.F90
  mediator/med_internalstate_mod.F90
  mediator/med_phases_profile_mod.F90
  mediator/esmFldsExchange_hafs_mod.F90
  mediator/med_phases_prep_rof_mod.F90
  mediator/esmFldsExchange_cesm_mod.F90
  mediator/med_merge_mod.F90
  mediator/med_constants_mod.F90
  mediator/med_kind_mod.F90
  mediator/esmFldsExchange_nems_mod.F90
  mediator/med_phases_prep_lnd_mod.F90
  mediator/med_phases_prep_atm_mod.F90
  mediator/med_phases_prep_ocn_mod.F90
  mediator/esmFlds.F90
  mediator/med.F90
  mediator/med_time_mod.F90
  mediator/med_phases_ocnalb_mod.F90
  mediator/med_phases_prep_wav_mod.F90
  mediator/med_utils_mod.F90
  mediator/med_fraction_mod.F90
  mediator/med_phases_aofluxes_mod.F90
  mediator/med_io_mod.F90)

### Package compiler flags
include(cmeps_compiler_flags)

### Package compilation properties
set(_inc_dir "include")
set(_mod_dir ${CMAKE_CURRENT_BINARY_DIR}/${_inc_dir})
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

### Use common object library for building shared and static targets
add_library(nems_util_obj OBJECT ${_nems_util_files})
set_target_properties(nems_util_obj PROPERTIES Fortran_MODULE_DIRECTORY ${_mod_dir})
target_include_directories(nems_util_obj PRIVATE $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/nems/util>)
target_link_libraries(nems_util_obj PRIVATE esmf
                                            PIO::PIO_C PIO::PIO_Fortran
                                            MPI::MPI_Fortran)
if(OpenMP_Fortran_FOUND)
  target_link_libraries(nems_util_obj PRIVATE OpenMP::OpenMP_Fortran)
endif()

add_library(mediator_obj OBJECT ${_mediator_src_files})
set_target_properties(mediator_obj PROPERTIES Fortran_MODULE_DIRECTORY ${_mod_dir})
target_include_directories(mediator_obj PRIVATE $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/mediator>)
list(APPEND _mediator_defs ESMF_VERSION_MAJOR=${ESMF_VERSION_MAJOR}
                           ESMF_VERSION_MINOR=${ESMF_VERSION_MINOR}
                           INTERNAL_PIO_INIT)
target_compile_definitions(mediator_obj PRIVATE "${_mediator_defs}")
target_link_libraries(mediator_obj PRIVATE nems_util_obj
                                           esmf
                                           PIO::PIO_C PIO::PIO_Fortran
                                           MPI::MPI_Fortran)
if(OpenMP_Fortran_FOUND)
  target_link_libraries(mediator_obj PRIVATE OpenMP::OpenMP_Fortran)
endif()

### Add static lib target
if(CMEPS_BUILD_STATIC_LIBS)
  add_library(${PROJECT_NAME}_static STATIC $<TARGET_OBJECTS:nems_util_obj>
                                            $<TARGET_OBJECTS:mediator_obj>)
  add_library(${PROJECT_NAME}::${PROJECT_NAME}_static ALIAS ${PROJECT_NAME}_static)
  list(APPEND _lib_targets ${PROJECT_NAME}_static)
endif()

### Add shared lib target
if(CMEPS_BUILD_SHARED_LIBS)
  add_library(${PROJECT_NAME}_shared SHARED $<TARGET_OBJECTS:nems_util_obj>
                                            $<TARGET_OBJECTS:mediator_obj>)
  add_library(${PROJECT_NAME}::${PROJECT_NAME}_shared ALIAS ${PROJECT_NAME}_shared)
  list(APPEND _lib_targets ${PROJECT_NAME}_shared)
endif()

### Set common lib target properties
set_target_properties(${_lib_targets} PROPERTIES OUTPUT_NAME ${PROJECT_NAME})
foreach( _tgt IN LISTS _lib_targets)
  target_compile_definitions(${_tgt} PUBLIC "${_mediator_defs}")
  target_include_directories(${_tgt} PUBLIC $<BUILD_INTERFACE:${_mod_dir}>
                                            $<INSTALL_INTERFACE:${_inc_dir}>)
  target_link_libraries(${_tgt} PUBLIC esmf
                                       PIO::PIO_C PIO::PIO_Fortran
                                       MPI::MPI_Fortran)
  if(OpenMP_Fortran_FOUND)
    target_link_libraries(${_tgt} PUBLIC OpenMP::OpenMP_Fortran)
  endif()
  set_property(TARGET ${_tgt} PROPERTY FOLDER ${PROJECT_NAME})
endforeach()

### Install
install(
  TARGETS ${_lib_targets}
  EXPORT ${PROJECT_NAME}Exports
  RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
  LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
  ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR})
install(DIRECTORY   ${_mod_dir}
        DESTINATION ${CMAKE_INSTALL_INCLUDEDIR})

### Package config
include(CMakePackageConfigHelpers)
set(CONFIG_INSTALL_DESTINATION lib/cmake/${PROJECT_NAME})

export(EXPORT ${PROJECT_NAME}Exports
  NAMESPACE ${PROJECT_NAME}::
  FILE ${PROJECT_NAME}-targets.cmake)

configure_package_config_file(
  ${CMAKE_SOURCE_DIR}/cmake/${PROJECT_NAME}Config.cmake.in ${CMAKE_BINARY_DIR}/${PROJECT_NAME}-config.cmake
  INSTALL_DESTINATION ${CONFIG_INSTALL_DESTINATION})
install(FILES ${CMAKE_BINARY_DIR}/${PROJECT_NAME}-config.cmake
  DESTINATION ${CONFIG_INSTALL_DESTINATION})

write_basic_package_version_file(
  ${CMAKE_BINARY_DIR}/${PROJECT_NAME}-config-version.cmake
  VERSION ${PROJECT_VERSION}
  COMPATIBILITY AnyNewerVersion)
install(FILES ${CMAKE_BINARY_DIR}/${PROJECT_NAME}-config-version.cmake
  DESTINATION ${CONFIG_INSTALL_DESTINATION})

install(EXPORT ${PROJECT_NAME}Exports
  NAMESPACE ${PROJECT_NAME}::
  FILE ${PROJECT_NAME}-targets.cmake
  DESTINATION ${CONFIG_INSTALL_DESTINATION})
