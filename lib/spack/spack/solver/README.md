# Clingo Concretizer / Solver

Clingo concretizer is based on Clingo, which is an *Answer Set Solver* (ASP), a system that finds all possible solutions to a set of facts and logical derivation rules. The concretizer translates dependencies and variants in a package recipe into *facts* in the Clingo language. These facts are then combines with a set of constraints and rules that apply for all the packages. At this point, Clingo system is executed to produce sets of resolved facts that specify concrete dependencies and variants, that is Clingo produces a set of stable *models* of specs. In the short description below concretizer and solver will be used interchangeably.

The directory contains three files:
* `asp.py` - Python code that drives Clingo and translates dependencies and variants in recipes to facts in Clingo.
* `concretize.lp` - a set of rules and constraints in Clingo that specify how a graph of dependencies is derived and concretized. For example, one rule specifies that a dependency chain ends with an external dependency.
* `display.lp` - a set of Clingo commands that specify which resolved facts will be written to the output. We are specifically interested in facts that form the concrete spec tree of a package. Otherwise, Clingo outputs all the facts, even the initial facts from the package recipe.

The `asp.py` class contains a number of classes:
* `SpackSolverSetup` - a class that sets up the solving process. Translates recipe directives such as `depends_on` into Clingo facts.
* `PyclingoDriver` - a driver for Clingo, which is essentially an interface that provides some helper functions for `SpackSolverSetup` and invokes the various stages of the process, i.e., grounding, solving.

