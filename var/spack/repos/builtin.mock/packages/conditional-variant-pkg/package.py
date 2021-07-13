# Copyright 2013-2021 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

class ConditionalVariantPkg(Package):
    """This package is used to test conditional variants."""
    homepage = "http://www.example.com/conditional-variant-pkg"
    url      = "http://www.unit-test-should-replace-this-url/conditional-variant-1.0.tar.gz"

    version('1.0', 'foobarbaz')
    version('2.0', 'bazbarfoo')

    variant('version_based', default=True, when='@2.0:',
            description="Check that version constraints work")

    variant('variant_based', default=False, when='+version_based',
            description="Check that variants can depend on variants")

    def install(self, spec, prefix):
        assert False
