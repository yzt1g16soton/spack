# Copyright 2013-2019 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)
import os
import sys

from llnl.util.filesystem import find_libraries, find_system_libraries

import spack.repo
import spack.error
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

    For libfoo.so, request ``libfoo``.
    """
    if not pkg_name:
        pkg_name = lib_name
    lib = find_library_in_environment(lib_name)
    if lib is None:
        pkg = find_pkg_ensure_installed(pkg_name)
        lib_paths = [os.path.join(pkg.prefix, libdir, lib_name)
                     for lib_name in ('lib', 'lib64')]
        lib_paths = list(filter(lambda p: os.path.exists(p), lib_paths))
        if not lib_paths:
            msg = 'Spack cannot find library %s' % lib_name
            msg += ' in package %s.\n' % pkg_name
            msg += 'Use an option which does not require this library.'
            raise spack.error.SpackError(msg)
        return lib_paths[0]
    else:
        return lib


def find_pkg_ensure_installed(pkg_name):
    spec = parse_specs(pkg_name, concretize=True)[0]
    pkg = spack.repo.get(spec)
    if not pkg.installed:
        pkg.do_install()
    return pkg


def find_library_in_environment(lib_name):
    lib_dir_env_var = 'DYLD_LIBRARY_PATH' if sys.platform == 'darwin' \
                      else 'LD_LIBRARY_PATH'
    if lib_dir_env_var not in os.environ:
        tty.msg('SANITIZED TO DEATH')
        return None
    libdirs = os.environ[lib_dir_env_var].split(':')
    for libdir in libdirs:
        lib_list = find_libraries(lib_name, libdir)  # shared, non-recursive
        if lib_name in map(lambda x: 'lib' + x, lib_list.names):
            return lib_list.libraries[0]
    tty.msg('TRY THE SYSTEM')
    return find_system_libraries(lib_name) or None
