.. Copyright 2013-2020 Lawrence Livermore National Security, LLC and other
   Spack Project Developers. See the top-level COPYRIGHT file for details.

   SPDX-License-Identifier: (Apache-2.0 OR MIT)

.. _concretizer_reference:

===========
Concretizer
===========

Spack can use different concretizers to pass from abstract specs to concrete ones.
Which one to use may be selected in ``config.yaml``.

.. _original_solver:

--------------------
Original Concretizer
--------------------

This is the concretizer Spack employs by default, and the one has been used since Spack first release.
It is greedy, does not do backtracking, and as a result the errors it gives can be confusing.
In many cases it can resolve a constraint too early -- it assigns final values to nodes as it
builds the graph, and it may assign a version, variant, or other value to a node without considering
the entire problem. This can result in the concretizer finding conflicts where solutions exist.
To select this concretizer add:

.. code-block:: yaml

   config:
     concretizer: original

to your ``config.yaml``.

.. note::

   Extending the current concretizer is difficult.  There are many moving pieces, and rewriting any
   of them can be a lot of work.  Making major changes to concretization semantics is difficult,
   and increasingly we're unable to add features that users need. In future major releases this
   concretizer is to be deprecated in favor of ones based on external solvers.

.. _asp_based_solver:

---------------------
ASP-Based Concretizer
---------------------

The ASP-based concretizer is experimental and makes use of
`Answer Set Programming <https://en.wikipedia.org/wiki/Answer_set_programming>`_.
It uses ``clingo``, the combined grounder (``gringo``) and solver (``clasp``)
from `Potassco <https://potassco.org/>`_, instead of attempting to do the entire solve
in Python as the :ref:`original_solver` does.
To use this concretizer you need to install:

.. code-block:: console

   $ spack install clingo@spack

get ``clingo`` on your ``PATH``, and finally add:

.. code-block:: yaml

   config:
     concretizer: clingo

to your ``config.yaml``.

^^^^^^^^^^^^
How it works
^^^^^^^^^^^^

Answer Set programming looks like `Prolog <https://en.wikipedia.org/wiki/Prolog>`_ but has
the advantage that, rather than trying to be a full programming language, it reduces logic
problems to `CDCL SAT <https://en.wikipedia.org/wiki/Conflict-driven_clause_learning>`_ with
optimization.  ASP has the nice property that solves will always terminate (unlike Prolog
programs), and it follows the `stable model semantics <https://en.wikipedia.org/wiki/Stable_model_semantics)>`_,
which makes it easier to model some of the default-driven behavior in Spack.

The new concretizer works like this:

1. Look at the input specs and read in *all possible dependencies*
2. Translate constraints in Spack's package DSL to rules and facts in ASP.  e.g., `zlib` has some facts like this:

  .. code-block::

     version_declared("zlib","1.2.11",0).
     version_declared("zlib","1.2.8",1).
     version_declared("zlib","1.2.3",2).

     variant("zlib","optimize").
     variant_single_value("zlib","optimize").
     variant_default_value_from_package_py("zlib","optimize","True").
     variant_possible_value("zlib","optimize","False").
     variant_possible_value("zlib","optimize","True").

   These come directly from `version()` and `variant()` directives in the `zlib/package.py` file.

3. Combine these facts with the logic program in `lib/spack/spack/solver/concretize.lp`.  This defines all the rules and optimization criteria used in concretization in Spack.
4. Send the whole program off to Clingo
5. Read back one the optimal stable model found by the solver, and build a concrete `Spec` from it.
