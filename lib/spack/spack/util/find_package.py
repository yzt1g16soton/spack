# Copyright 2013-2019 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)
import os

import spack.repo
from spack.util.executable import which
from spack.cmd import parse_specs


def find_executable(exe_name, pkg_name=None):
    """Ensure executable exe_name from package pkg_name is available.

    Check the user PATH for the variable, otherwise ensure it is installed
    through Spack
    """
    if not pkg_name:
        pkg_name = exe_name
    exe = which(exe_name)
    if exe is None:
        pkg = find_pkg_ensure_installed(pkg_name)
        exe_path = os.path.join(pkg.prefix.bin, exe_name)
        return exe_path
    else:
        return exe.path


def find_library(lib_name, pkg_name=None):
    """Ensure library lib_name from package pkg_name is available

    Check the user LD_LIBRARY_PATH for the library, otherwise ensure it is
    installed through Spack
    """
    if not pkg_name:
        pkg_name = lib_name
    lib = TODO_find_lib
    if lib is None:
        pkg = find_pkg_ensure_installed(pkg_name)
        lib_paths = [os.path.join(pkg.prefix, libdir, lib_name)
                     for lib_name in ('lib', 'lib64')]
        lib_paths = list(filter(lambda p: os.path.exists(p), lib_paths))
        return lib_paths[0] if lib_paths else None
    else:
        return lib


def find_pkg_ensure_installed(pkg_name):
    spec = parse_specs(pkg_name, concretize=True)[0]
    pkg = spack.repo.get(spec)
    if not pkg.installed:
        pkg.do_install()
    return pkg


def find_library_in_environment(lib_name):
    lib_dir_env_var = 'DYLD_LIBRARY_PATH' if sys.platform() == 'Darwin' \
                      else 'LD_LIBRARY_PATH'
    if lib_dir_env_var not in os.environ:
        return None
    libdirs = os.environ[lib_dir_env_var].split(':')
    for libdir in libdirs:
        candidate = os.path.join(libdir, lib_name)
        if os.path.exists(candidate):
            return candidate
    return None
