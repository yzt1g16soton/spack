# Copyright 2013-2019 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack import *


class Sandbox(AutotoolsPackage):
    """sandbox'd LD_PRELOAD hack by Gentoo Linux"""

    homepage = "https://www.gentoo.org/proj/en/portage/sandbox/"
    url      = "https://gitweb.gentoo.org/proj/sandbox.git/snapshot/sandbox-2.13.tar.gz"

    depends_on('m4')
    depends_on('libtool')
    depends_on('autoconf')
    depends_on('automake@1.14:')

    version('2.17', sha256='44c8be0381d7dc58630c71361f0a43abba289fd95411f592ee5a9ec665f68f45')
    version('2.16', sha256='973e5fff39d5f74781543900d74985fe44a2db89f1d0cfb3518147e377269c2c')
    version('2.15', sha256='c9edf1e4696ee1da252240115ec9712c11f7226f425b1ad733e03add7dac2fbb')
    version('2.14', sha256='1fa4874a818d3add34893acc95ab6d4ea3ccdfa9101ac5fcdda664ce642cb25f')
    version('2.13', sha256='673892b35b5358819f0e41804c0f0a9e70d242a1db269dafd6ceac92d0e83c55')
    version('2.12', sha256='32b867652fc535068f07c3ae95b16c11487f1e57187d5aa4210e928e7e07e2fa')
